
import frappe
from frappe import _
from datetime import datetime
from frappe.query_builder import Order

def execute(filters=None):
    try:
        if filters["scholarship"]:
            columns, data = scholarship_columns(), scholarship_data(filters)
    except:
        columns, data = get_columns(), get_salary_slips(filters)
        if filters.get('employee'):
            for val in data:
                if not val.get('status') and not val.get('employee'):
                    columns.pop(3)
                    break
        
    return columns, data


from datetime import datetime

def get_salary_slips(filters):
    add_salary = frappe.qb.DocType("Additional Salary")
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    query = (
        frappe.qb.from_(add_salary)
        .select(add_salary.employee, add_salary.employee_name, add_salary.payroll_date, add_salary.salary_component, add_salary.amount)
        .where(add_salary.docstatus == doc_status["Submitted"])
        .orderby(add_salary.employee)       
    )

    if filters.get("from_date") and filters.get("to_date"):
        query = query.where(add_salary.payroll_date.between(filters["from_date"], filters["to_date"]))
    if filters.get("company"):
        query = query.where(add_salary.company == filters["company"])
    if filters.get("employee"):
        query = query.where(add_salary.employee == filters["employee"])
    if filters.get("salary_component"):
        query = query.where(add_salary.salary_component == filters["salary_component"])

    add_salaries = query.run(as_dict=1)

    result = []
    last_employee = None
    last_employee_name = None
    last_component = None
    last_amount = None
    from_date = None

    for salary in add_salaries:  
        if last_employee == salary["employee"]:
            if last_component == salary["salary_component"]:
                if last_amount != salary["amount"]:
                    result.append({
                        "salary_component": last_component,
                        "from_payroll_date": from_date,
                        "to_payroll_date": salary["payroll_date"].strftime("%d-%m-%Y"),
                        "amount": last_amount,
                        'indent':1
                    })
                
                    from_date = salary["payroll_date"]
                    last_amount = salary["amount"]
            else:
                result.append({
                    "salary_component": last_component,
                    "from_payroll_date": from_date,
                    "to_payroll_date": "Present",
                    "amount": last_amount,
                    'indent':1
                })
                from_date = salary["payroll_date"]
                last_component = salary["salary_component"]
                last_amount = salary["amount"]

        else:
            if last_employee is not None:
                result.append({
                    "salary_component": last_component,
                    "from_payroll_date": from_date,
                    "to_payroll_date": "Present",
                    "amount": last_amount,
                    'indent':1
                })
            result.append({
                "employee": salary["employee"],
                "employee_name": salary["employee_name"],
                'indent':0
            })
            from_date = salary["payroll_date"]
            last_employee = salary["employee"]
            last_employee_name = salary["employee_name"]
            last_component = salary["salary_component"]
            last_amount = salary["amount"]

    if last_employee is not None:
        result.append({
            "salary_component": last_component,
            "from_payroll_date": from_date,
            "to_payroll_date": "Present",
            "amount": last_amount,
            'indent':1
        })
    emp = None
    if result:
        for record in result:
            if not record['indent']:
                emp = record['employee']
            if frappe.db.get_all('Scholarship',{'employee':emp}):
               
                if record['indent']:
                    if frappe.db.get_all('Scholarship',{'employee':emp,'start_date':("<=", record['from_payroll_date']),'end_date':(">=", record['from_payroll_date'])}):
                        record['status'] = 'Suspended'
                    else:
                        record['status'] = 'Active'
            else:
                record['status'] = ''
    return result


def get_columns():
    columns = [
		{
			"label": _("Employee Id"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 250,
		},
        {
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("Salary Component"),
			"fieldname": "salary_component",
			"fieldtype": "Link",
			"options": "Salary Component",
			"width": 250,
		},
        {
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("From Date"),
			"fieldname": "from_payroll_date",
			"fieldtype": "Date",
			"width": 250,
		},
        {
			"label": _("To Date"),
			"fieldname": "to_payroll_date",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 250,
		},
        ] 
    return columns

def scholarship_columns():
    columns = [
		{
			"label": _("Employee Id"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 250,
		},
        {
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("Scholarship Type"),
			"fieldname": "scholarship_type",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("Processing Status"),
			"fieldname": "processing",
			"fieldtype": "Data",
			"width": 250,
		},
        {
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 250,
		},
        {
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 250,
		},
        ]
    return columns

def scholarship_data(filters):
    add_salary = frappe.qb.DocType("Scholarship")
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    query = (
        frappe.qb.from_(add_salary)
        .select(add_salary.employee, add_salary.employee_name, add_salary.processing, add_salary.scholarship_type, add_salary.start_date, add_salary.end_date, add_salary.scholarship_id)
        .where(add_salary.docstatus == doc_status["Submitted"])
        .orderby(add_salary.employee)       
    )

    if filters.get("from_date") and filters.get("to_date"):
        query = query.where(add_salary.start_date.between(filters["from_date"], filters["to_date"]))
    # if filters.get("company"):
    #     query = query.where(add_salary.company == filters["company"])
    if filters.get("employee"):
        query = query.where(add_salary.employee == filters["employee"])
    # if filters.get("salary_component"):
    #     query = query.where(add_salary.salary_component == filters["salary_component"])
    add_salaries = query.run(as_dict=1)
   
    result = []
    if add_salaries:
        for salary in add_salaries:
            try:
                if not salary['scholarship_id']:
                    result.append({
                        "employee": salary["employee"],
                        "employee_name": salary["employee_name"],
                        "scholarship_type": salary['scholarship_type'],
                        'indent':0
                    })
                result.append({
                                "processing": salary['processing'],
                                'start_date':salary['start_date'],
                                'end_date':salary['end_date'],
                                'indent':1
                            })
            except Exception as err:
                pass
    return result