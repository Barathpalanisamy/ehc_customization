import frappe
import io
import pandas as pd
from frappe import _

def validate_file(self):
    if self.reference_doctype == "Additional Salary":
        if not self.marge_file_attach:
            self.import_file = ''

        if self.is_merge and self.marge_file_attach:
            column_mapping_doc = frappe.get_doc("Data Import Settings", 'Data Import Settings').as_dict()
            column_mapping = column_mapping_doc.get('column_mapping', {})
            file = frappe.get_doc("File", {'file_url': self.marge_file_attach})
            file_doc = file.get_content()
            unmerged_file_doc = unmerge_cells(self, file_doc, file.file_name, column_mapping)
            self.import_file = unmerged_file_doc.file_url

def unmerge_cells(self, file_content, original_filename, column_mapping):

    new_file_list = []

    compare = frappe.get_doc('Data Import Settings','Data Import Settings')
    if compare.compare_national_id:
        new_file_list.append("National ID")
    if compare.compare_salary_component:
        new_file_list.append("Salary Component",)   

    if not column_mapping:
        frappe.throw(_("Please map the column headings in Data Import Settings."))

    if original_filename.endswith('.xlsx'):
        df = pd.read_excel(io.BytesIO(file_content))
    elif original_filename.endswith('.csv'):
        if isinstance(file_content, str):
            file_content = file_content.encode()
        df = pd.read_csv(io.BytesIO(file_content))
    else:
        return None
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.columns = ['New ' + col[:-2] if col.endswith('.1') else col for col in df.columns]
    
    df['row_num'] = df.index + 1
    

    df = rename_columns(df, column_mapping)
    # Split columns into rows
    df = df.fillna(method="ffill")

    df = split_columns_to_rows(df,self)

    
    df.drop(columns=['Basic Salary'], inplace=True)



    if new_file_list:
        grouped_df = df.groupby(new_file_list, as_index=False).agg({
            **{col: 'first' for col in df.columns},  # Keep all columns
            'Amount': 'sum',
            'row_num': lambda x: ', '.join(str(row) for row in x)
        })
        grouped_df['custom_salary_merging'] = grouped_df.apply(lambda row: " + ".join([f"Row {int(row_num)} ({df.loc[int(row_num)-1, 'Amount']})" for row_num in row['row_num'].split(",")]) + " = " + str(row['Amount']) if len(row['row_num'].split(',')) > 1 else '', axis=1)
    else:
        grouped_df = df
    
    grouped_df.drop(columns=['row_num'], inplace=True)
    mapping_dict = {item['new_column'] for item in column_mapping}
    unmapped_columns = [col for col in grouped_df.columns if col not in mapping_dict]
    if unmapped_columns:
        exclude_columns = ["Employee", "Payroll Date", "custom_salary_merging"]
        unmapped_columns = [col for col in unmapped_columns if col not in exclude_columns]
        if unmapped_columns:
            frappe.msgprint(_('There are {0} columns not mapped: {1}').format(len(unmapped_columns), ', '.join(unmapped_columns)), alert=True)
    mapped_columns = [col for col in grouped_df.columns if col in mapping_dict]

    # Add custom columns to the mapped columns list
    custom_columns = ["Payroll Date", "Employee"]
    last_column = ['custom_salary_merging']
    final_columns = custom_columns + mapped_columns + last_column

    new_file = save_to_file(grouped_df[final_columns], original_filename)
    
    

    # new_file = save_to_file(grouped_df, original_filename)

    return new_file
def rename_columns(df, column_mapping):
    mapping_dict = {}
    for item in column_mapping:
        import_column = item['import_file_column']
        new_column = item['new_column']

        if import_column in mapping_dict:
            suffix = 1
            while f"{import_column}.{suffix}" in mapping_dict:
                suffix += 1
            import_column = f"New {import_column}"

        mapping_dict[import_column] = new_column

    df.rename(columns=mapping_dict, inplace=True)
    
    return df

def split_columns_to_rows(df, self):
    payroll_date = self.custom_payroll_date
    new_df = pd.DataFrame(columns=['Employee', 'Salary Component', 'Amount', 'Payroll Date'] + list(df.columns.difference(['Employee', 'Salary Component', 'Amount', 'Payroll Date'])))
    basic_added_for_employee = set()  
    component_added_for_employee = {}  
    for index, row in df.iterrows():
        national_id = row.get('National ID')
        if national_id:
            # Fetch the employee ID using the national ID
            employees = frappe.get_all("Employee", filters={'nat_id': national_id}, fields=['name'])
            if employees:
                employee_name = employees[0]['name']
            else:
                employee_name = None
        else:
            employee_name = None
        for col_name, value in row.items():
            # Check if the value is not NaN
            if pd.notna(value):
                # If the value is in a column containing "Salary", update the salary_component variable
                if "Salary Component" in col_name:
                    salary_component = value
                # If the value is in a column containing "Amount", add a new row to the DataFrame
                elif "Amount" in col_name:
                    # Check if the component has already been added for this employee with the same amount
                    if (employee_name, salary_component) not in component_added_for_employee or component_added_for_employee[(employee_name, salary_component)] != value:
                        new_row = [employee_name, salary_component, value, payroll_date]
                        for other_col in df.columns.difference(['Employee', 'Salary Component', 'Amount', 'Payroll Date']):
                            new_row.append(row[other_col])
                        new_df.loc[len(new_df)] = new_row
                        component_added_for_employee[(employee_name, salary_component)] = value  # Mark component as added with its amount
        # If 'Basic Salary' column exists and it hasn't been added for this employee yet, add an extra row for 'Basic' component
        if 'Basic Salary' in row and employee_name not in basic_added_for_employee:
            name_basic = frappe.get_all("Salary Component", {'ehc_name_in_arabic': "Basic"}, pluck='name')
            basic_amount = row['Basic Salary']
            if (employee_name,'الراتب الأساسي') not in component_added_for_employee or component_added_for_employee[(employee_name, 'الراتب الأساسي')] != basic_amount:
                new_row = [employee_name,'الراتب الأساسي', basic_amount, payroll_date]
                for other_col in df.columns.difference(['Employee', 'Salary Component', 'Amount', 'Payroll Date']):
                    new_row.append(row[other_col])
                new_df.loc[len(new_df)] = new_row
                basic_added_for_employee.add(employee_name)  # Add employee to the set to indicate 'Basic Salary' added
                component_added_for_employee[(employee_name,'الراتب الأساسي')] = basic_amount  # Mark component as added with its amount
    return new_df


def save_to_file(df, original_filename):
    temp_output_file = io.BytesIO()

    if original_filename.endswith('.xlsx'):
        df.to_excel(temp_output_file, index=False)
    elif original_filename.endswith('.csv'):
        df.to_csv(temp_output_file, index=False)

    temp_output_file.seek(0)
    new_file = frappe.new_doc("File")
    new_file.update({
        "file_name": original_filename,
        "is_private": 1,
        "content": temp_output_file.getvalue()
    })
    new_file.save()

    return new_file

@frappe.whitelist()
def get_additional_salary_fields():
    additional_salary_fields = frappe.get_meta("Additional Salary").get("fields")
    fields = [field.label for field in additional_salary_fields if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']]
    return fields
