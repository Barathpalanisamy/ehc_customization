
import frappe
from frappe import _
from datetime import datetime
from frappe.query_builder import Order

def execute(filters=None):
    columns, data = get_columns(), get_salary_slips(filters)
    return columns, data

def get_salary_slips(filters):
	add_salary = frappe.qb.DocType("Salary Structure Assignment")
	salary_structure = frappe.qb.DocType("Salary Structure")
	salary_details = frappe.qb.DocType("Salary Detail")
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = (
		frappe.qb.from_(add_salary)
		.left_join(salary_structure)
		.on(add_salary.salary_structure == salary_structure.name)
		.inner_join(salary_details)
		.on(salary_structure.name == salary_details.parent)
		.select(add_salary.employee, add_salary.employee_name, add_salary.from_date, add_salary.salary_structure,salary_details.salary_component,salary_details.amount,salary_details.parentfield)
		.where(add_salary.docstatus == doc_status["Submitted"])
		.orderby(add_salary.employee)       
	)

	if filters.get("from_date"):
		query = query.where(add_salary.from_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(add_salary.from_date <= filters["to_date"])
	if filters.get("company"):
		query = query.where(add_salary.company == filters["company"])
	if filters.get("employee"):
		query = query.where(add_salary.employee == filters["employee"])
	if filters.get("salary_component"):
		query = query.where(salary_details.salary_component == filters["salary_component"])

	add_salarys = query.run(as_dict=1)
	result = []
	last_salary_structure = None

	for salary in add_salarys:
		check_scholarship = frappe.db.get_all('Scholarship', {
			'employee': salary.employee, 
			'docstatus': 0,
			'start_date': ['>=', salary.from_date],
			# 'end_date': ['<=', salary.from_date]
			}, ['scholarship_type'])
		if check_scholarship:
			if last_salary_structure != salary.salary_structure:
				result.append({
						"employee": salary["employee"],
						"employee_name": salary["employee_name"],
						'indent':0
						})
			result.append({
						"salary_component": salary.salary_component,
						"from_payroll_date": frappe.db.get_value('Scholarship', {
						'employee': salary.employee, 
						'docstatus': 0,
						'start_date': ['>=', salary.from_date],
						'end_date': ['>=', salary.from_date]
						}, ['start_date']),
						"to_payroll_date": frappe.db.get_value('Scholarship', {
						'employee': salary.employee, 
						'docstatus': 0,
						'start_date': ['>=', salary.from_date],
						'end_date': ['>=', salary.from_date]
						}, ['end_date']),
						"amount": salary.amount * 0.5 if check_scholarship[0].scholarship_type == 'Scholarship' and salary.salary_component =='Basic' else salary.amount,
						"status": 'Active' if salary.salary_component =='Basic' or salary.parentfield=='deductions' else "Suspended",
						'indent':1

					})
		else:
			if last_salary_structure != salary.salary_structure:
				result.append({
						"employee": salary["employee"],
						"employee_name": salary["employee_name"],
						'indent':0
						})
			result.append({
						"salary_component": salary.salary_component,
						"from_payroll_date": salary.from_date,
						"to_payroll_date": datetime.today().strftime('%Y-%m-%d'),
						"amount": salary.amount,
						"status": "Actual Period",
						'indent':1

					})

		last_salary_structure = salary.salary_structure
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
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		},
        {
			"label": _("Salary Component"),
			"fieldname": "salary_component",
			"fieldtype": "Link",
			"options": "Salary Component",
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
			"fieldtype": "Date",
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

