import frappe
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from ehc_customization.ehc_customization.customizations.payroll_entry.override.payroll_override import  change_paid_status_to_none, fill_employee_details, get_account_custom,get_emp_list,get_salary_component_total_custom, make_accrual_jv_entry_custom,custom_validate_employee_details

class payrollentryoverride(PayrollEntry):
	def get_emp_list(self):
		get_emp_list(self)

	@frappe.whitelist()
	def fill_employee_details(self):
		fill_employee_details(self)

	def make_accrual_jv_entry(self, submitted_salary_slips):
		make_accrual_jv_entry_custom(self, submitted_salary_slips)

	def before_submit(self):
		custom_validate_employee_details(self)
	
def on_cancel(self,action):
	change_paid_status_to_none(self)




	



