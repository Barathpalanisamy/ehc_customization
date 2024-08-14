from hrms.payroll.doctype.salary_slip.salary_slip import  SalarySlip
import frappe
from ehc_customization.ehc_customization.customizations.salary_slip.doc_events.custom_salaryslip import change_paid_status_to_none, override_salary_components,change_paid_status
from ehc_customization.ehc_customization.customizations.salary_slip.override.override_salaryslip import override_validate, custom_calculate_net_pay,custom_calculate_component_amounts,custom_get_working_days_details

class salaryslip_override(SalarySlip):
    def validate(self):
        override_validate(self)

    def calculate_net_pay(self):
        custom_calculate_net_pay(self)

    def calculate_component_amounts(self,component_type):
        custom_calculate_component_amounts(self,component_type)

    def get_working_days_details(self, joining_date=None, relieving_date=None, lwp=None, for_preview=0):
        custom_get_working_days_details(self, joining_date, relieving_date, lwp, for_preview)
    
def validate(doc,action):
    override_salary_components(doc)


def on_submit(doc,action):
    change_paid_status(doc)
def on_cancel(doc,action):
    change_paid_status_to_none(doc)

