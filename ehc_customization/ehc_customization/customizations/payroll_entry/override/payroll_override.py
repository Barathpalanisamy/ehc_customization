from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from frappe.query_builder.functions import Coalesce
from frappe.query_builder import Criterion
import frappe
import erpnext
from frappe.utils import flt
from frappe import _
from frappe.utils.data import get_link_to_form
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_salary_structure, remove_payrolled_employees


def make_filters_custom(self):
	filters = frappe._dict()
	filters["company"] = self.company
	filters["branch"] = self.branch
	filters["department"] = self.department
	filters["designation"] = self.designation
	filters["payroll_structure"] = self.payroll_structure
	
	return filters

def get_emp_list(self):
		"""
		Returns list of active employees based on selected criteria
		and for which salary structure exists
		"""
		# self.check_mandatory()
		filters = make_filters_custom(self)
		# cond += get_joining_relieving_condition(self.start_date, self.end_date)

		sal_struct = get_salary_structure(
			self.company, self.currency, self.salary_slip_based_on_timesheet, self.payroll_frequency
		)
		if sal_struct:
			emp_list = get_emp_list_custom(sal_struct, filters,self.start_date, self.end_date, self.payroll_payable_account)
			# emp_list = remove_payrolled_employees(emp_list, self.start_date, self.end_date)
			return emp_list




def get_emp_list_custom(sal_struct, filters, start_date,end_date, payroll_payable_account):
	employee=frappe.qb.DocType("Employee")
	salary_st=frappe.qb.DocType("Salary Structure Assignment")
	cond=[]
	if filters.get("company"):
		cond.append(employee.company==filters.get("company"))
	if filters.get("branch"):
		cond.append(employee.branch==filters.get("branch"))
	if filters.get("department"):
		cond.append(employee.department==filters.get("department"))
	if filters.get("payroll_structure"):
		cond.append(employee.payroll_structure==filters.get("payroll_structure"))
	if filters.get("designation"):
		cond.append(employee.designation==filters.get("designation"))

	if start_date:
		cond.append(Coalesce(employee.date_of_joining, "1900-01-01") <= end_date)
	if end_date:
		cond.append(Coalesce(employee.relieving_date, "2199-12-31") >= start_date)

	query=(
		frappe.qb.from_(employee)
		.join(salary_st)
		.on(employee.name==salary_st.employee)
	  	.select(employee.name.as_("employee")
		,employee.department,
		 employee.employee_name,
		 employee.designation).distinct()
		 .where(salary_st.docstatus==1)
		 .where(employee.status!= "Inactive")
		 .where(salary_st.payroll_payable_account==payroll_payable_account)
		 .where(salary_st.salary_structure.isin(sal_struct))
		 .where(salary_st.from_date <=end_date)
		 .where(Criterion.all(cond))
		 .orderby(salary_st.from_date, order=frappe.qb.desc)
	  	).run(as_dict=True)
	return query

def remove_payrolled_employees(emp_list, start_date, end_date):
	new_emp_list = []
	for employee_details in emp_list:
		if not frappe.db.exists(
			"Salary Slip",
			{
				"employee": employee_details.employee,
				"start_date": start_date,
				"end_date": end_date,
				"docstatus": 1,
			},
		):
			new_emp_list.append(employee_details)

	return new_emp_list

@frappe.whitelist()
def fill_employee_details(self):
	self.set("employees", [])
	employees = get_emp_list(self)
	if not employees:
		error_msg = _(
			"No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>Payroll Payable Account: {2}"
		).format(
			frappe.bold(self.company),
			frappe.bold(self.currency),
			frappe.bold(self.payroll_payable_account),
		)
		if self.branch:
			error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
		if self.department:
			error_msg += "<br>" + _("Department: {0}").format(frappe.bold(self.department))
		if self.designation:
			error_msg += "<br>" + _("Designation: {0}").format(frappe.bold(self.designation))
		if self.start_date:
			error_msg += "<br>" + _("Start date: {0}").format(frappe.bold(self.start_date))
		if self.end_date:
			error_msg += "<br>" + _("End date: {0}").format(frappe.bold(self.end_date))
		frappe.throw(error_msg, title=_("No employees found"))

	for d in employees:
		self.append("employees", d)

	self.number_of_employees = len(self.employees)
	return self.get_employees_with_unmarked_attendance()


def make_accrual_jv_entry_custom(self, submitted_salary_slips):
		self.check_permission("write")
		process_payroll_accounting_entry_based_on_employee = frappe.db.get_single_value(
			"Payroll Settings", "process_payroll_accounting_entry_based_on_employee"
		)
		self.employee_based_payroll_payable_entries = {}
		self._advance_deduction_entries = []

		earnings = (
			get_salary_component_total_custom(
				self,
				component_type="earnings",
				process_payroll_accounting_entry_based_on_employee=process_payroll_accounting_entry_based_on_employee,
			)
			or {}
		)

		deductions = (
			get_salary_component_total_custom(
				self,
				component_type="deductions",
				process_payroll_accounting_entry_based_on_employee=process_payroll_accounting_entry_based_on_employee,
			)
			or {}
		)

		payroll_payable_account = self.payroll_payable_account
		jv_name = ""
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		if earnings or deductions:
			journal_entry = frappe.new_doc("Journal Entry")
			journal_entry.voucher_type = "Journal Entry"
			journal_entry.user_remark = _("Accrual Journal Entry for salaries from {0} to {1}").format(
				self.start_date, self.end_date
			)
			journal_entry.company = self.company
			journal_entry.posting_date = self.posting_date
			accounting_dimensions = get_accounting_dimensions() or []

			accounts = []
			currencies = []
			payable_amount = 0
			multi_currency = 0
			company_currency = erpnext.get_company_currency(self.company)
			
			# Earnings
			for earning in earnings:
				for acc_cc, amount in earning.items():
					payable_amount = self.get_accounting_entries_and_payable_amount(
						acc_cc[0],
						acc_cc[1] or self.cost_center,
						amount,
						currencies,
						company_currency,
						payable_amount,
						accounting_dimensions,
						precision,
						entry_type="debit",
						accounts=accounts,
					)


			# Deductions
			for deductions in deductions:
				for acc_cc, amount in deductions.items():
					payable_amount = self.get_accounting_entries_and_payable_amount(
						acc_cc[0],
						acc_cc[1] or self.cost_center,
						amount,
						currencies,
						company_currency,
						payable_amount,
						accounting_dimensions,
						precision,
						entry_type="credit",
						accounts=accounts,
					)

			payable_amount = self.set_accounting_entries_for_advance_deductions(
				accounts,
				currencies,
				company_currency,
				accounting_dimensions,
				precision,
				payable_amount,
			)

			# Payable amount
			if process_payroll_accounting_entry_based_on_employee:

				"""
				employee_based_payroll_payable_entries = {
				        'HR-EMP-00004': {
				                        'earnings': 83332.0,
				                        'deductions': 2000.0
				                },
				        'HR-EMP-00005': {
				                'earnings': 50000.0,
				                'deductions': 2000.0
				        }
				}
				"""
				for employee, employee_details in self.employee_based_payroll_payable_entries.items():
					payable_amount = employee_details.get("earnings", 0) - employee_details.get("deductions", 0)

					payable_amount = self.get_accounting_entries_and_payable_amount(
						payroll_payable_account,
						self.cost_center,
						payable_amount,
						currencies,
						company_currency,
						0,
						accounting_dimensions,
						precision,
						entry_type="payable",
						party=employee,
						accounts=accounts,
					)

			else:
				payable_amount = self.get_accounting_entries_and_payable_amount(
					payroll_payable_account,
					self.cost_center,
					payable_amount,
					currencies,
					company_currency,
					0,
					accounting_dimensions,
					precision,
					entry_type="payable",
					accounts=accounts,
				)

			journal_entry.set("accounts", accounts)
			if len(currencies) > 1:
				multi_currency = 1
			journal_entry.multi_currency = multi_currency
			journal_entry.title = payroll_payable_account
			journal_entry.save()
			try:
				journal_entry.submit()
				jv_name = journal_entry.name
                                #if submitted_salary_slips:
				self.update_salary_slip_status(submitted_salary_slips, jv_name=jv_name)
			except Exception as e:
				if type(e) in (str, list, tuple):
					frappe.msgprint(e)
				raise

		return jv_name


def get_account_custom(self, component_dict=None,final_list=None):
	final_list=final_list
	account_dict = {}
	job_category_value = component_dict.get('job_category')
	for key, amount in component_dict.items():
		account_dict = {}
		if key == 'job_category':
			continue 
		component, cost_center = key
		account = get_salary_component_account_custom(self,component, job_category_value)
		accounting_key = (account, cost_center)
		
		account_dict[accounting_key] = amount
		
		final_list.append(account_dict)
	
	return final_list

def get_salary_component_total_custom(
		self,
		component_type=None,
		process_payroll_accounting_entry_based_on_employee=False,
	):
		salary_components = self.get_salary_components(component_type)
		if salary_components:
			
			final_list=[]
			for item in salary_components:
				component_dict = {}
				if item.employee:
						job_category = frappe.get_value("Employee", item.employee, "financial_job_category")
						component_dict["job_category"] = job_category
				if not self.should_add_component_to_accrual_jv(component_type, item):
					continue

				employee_cost_centers = self.get_payroll_cost_centers_for_employee(
					item.employee, item.salary_structure
				)
				employee_advance = self.get_advance_deduction(component_type, item)

				for cost_center, percentage in employee_cost_centers.items():
					amount_against_cost_center = flt(item.amount) * percentage / 100

					if employee_advance:
						self.add_advance_deduction_entry(
							item, amount_against_cost_center, cost_center, employee_advance
						)
					else:
						key = (item.salary_component, cost_center)
						component_dict[key] =amount_against_cost_center

					if process_payroll_accounting_entry_based_on_employee:
						self.set_employee_based_payroll_payable_entries(
							component_type, item.employee, amount_against_cost_center
						)
					

				account_details = get_account_custom(self,component_dict=component_dict,final_list=final_list)

			return account_details
		
def get_salary_component_account_custom(self,salary_component,job_category_value):
		account = frappe.db.get_value(
			"Salary Component Account", {"parent": salary_component, "company": self.company,"financial_job_category":job_category_value}, "account"
		)

		if not account:
			frappe.throw(
				_(".Please set account in Salary Component {0}").format(
					get_link_to_form("Salary Component", salary_component)
				)
			)
		return account


def custom_validate_employee_details(self):
		emp_with_sal_slip = []
		for employee_details in self.employees:
			if frappe.db.exists(
				"Salary Slip",
				{
					"employee": employee_details.employee,
					"start_date": self.start_date,
					"end_date": self.end_date,
					"docstatus": 1,
				},
			):
				emp_with_sal_slip.append(employee_details.employee)

		# if len(emp_with_sal_slip):
		# 	frappe.throw(_("Salary Slip already exists for {0}").format(comma_and(emp_with_sal_slip)))


def change_paid_status_to_none(doc):
    add_salary = frappe.get_all("Additional Salary",{"custom_payroll_entry":doc.name,"custom_paid_additional_salary":1,"docstatus": ["!=", 0]},pluck='name')
    for i in add_salary:
        frappe.db.set_value("Additional Salary",i,"custom_paid_additional_salary",0)
        frappe.db.set_value("Additional Salary",i,"custom_salary_slip",'')
        frappe.db.set_value("Additional Salary",i,"custom_payroll_entry",'')
