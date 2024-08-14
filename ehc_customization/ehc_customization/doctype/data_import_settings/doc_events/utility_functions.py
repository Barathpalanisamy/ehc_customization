import frappe
import pandas as pd
import io
import difflib
def import_columns(self):
    if not self.attach :
        self.column_mapping =[]
    if self.attach and not self.column_mapping:
        file = frappe.get_doc("File", {'file_url': self.attach})
        file_content = file.get_content()
        if file.file_name.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_content))
        elif file.file_name.endswith('.csv'):
            if isinstance(file_content, str):
                file_content = file_content.encode()
            df = pd.read_csv(io.BytesIO(file_content))
        self.column_mapping =[]
        additional_salary_fields = frappe.get_meta("Additional Salary").get("fields")
        fields = [field.label for field in additional_salary_fields if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']]
        for index, row in df.iterrows():
            for value in row:
                matching_option = difflib.get_close_matches(value, fields, n=1)
                if matching_option:
                    self.append("column_mapping", {
                        'import_file_column': value,
                        'new_column': matching_option[0]
                    })
                    self.flags.ignore_mandatory = True
                else:
                    self.append("column_mapping", {
                        'import_file_column': value,
                    })
                    self.flags.ignore_mandatory = True

