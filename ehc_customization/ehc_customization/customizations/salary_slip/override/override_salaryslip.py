import frappe
from hrms.payroll.doctype.payroll_period.payroll_period import (
	get_period_factor,
)
from frappe.utils import flt,get_datetime,add_days,cint,date_diff,getdate
import datetime
from hrms.hr.utils import validate_active_employee
from frappe import _, msgprint
import calendar
from hrms.payroll.doctype.salary_slip.salary_slip_loan_utils import (
        cancel_loan_repayment_entry,
        make_loan_repayment_entry,
        set_loan_repayment,
)

def custom_calculate_net_pay(self):
    if self.salary_structure:
        self.calculate_component_amounts("earnings")

    # get remaining numbers of sub-period (period for which one salary is processed)
    if self.payroll_period:
        self.remaining_sub_periods = get_period_factor(
            self.employee, self.start_date, self.end_date, self.payroll_frequency, self.payroll_period
        )[1]

    if self.docstatus != 2:
        try:
            if self.deductions:
                for deduction in self.deductions:
                    deduction.amount = deduction.additional_amount 

            basic_earnings = []
            gross = 1
            for earning in self.earnings:
                additional_date = frappe.db.get_value('Additional Salary', {'name':earning.additional_salary, 'docstatus':1},['payroll_date'])
                if additional_date:
                    check_scholarship = frappe.db.get_all('Scholarship',{'docstatus':1, 'employee':self.employee,'start_date':("<=", additional_date),'end_date':(">=", additional_date)},['*'])
                else:
                    check_scholarship = frappe.db.get_all('Scholarship',{'docstatus':1, 'employee':self.employee,'start_date':(">=", self.start_date),'end_date':("<=", self.end_date)},['*'])
                
                if earning.additional_amount and earning.additional_amount < 0:
                    earning.amount = ((earning.amount) / self.total_working_days) * self.payment_days

                if check_scholarship:
                    self.payment_days = self.payment_days + self.leave_without_pay
                    self.leave_without_pay = 0
                    if earning.salary_component in ['Basic', 'الراتب الأساسي']:
                        if check_scholarship[0].scholarship_type == 'Internal Dispatch':
                            earning.amount = earning.additional_amount if earning.additional_amount else earning.default_amount
                        else:
                            earning.amount = (earning.additional_amount if earning.additional_amount else earning.default_amount)  * 0.5
                            gross = 0.5
                        earning.year_to_date = earning.amount   
                        basic_earnings.append(earning) 
                    else:
                        month_days = calendar.monthrange(check_scholarship[0]['start_date'].year, check_scholarship[0]['start_date'].month)[1]
                        diff = month_days - ((((check_scholarship[0]['end_date'] - check_scholarship[0]['start_date'])).days) + 1)
                        if diff:

                            if check_scholarship[0].scholarship_type == 'Internal Dispatch':
                                earning.amount = (earning.additional_amount if earning.additional_amount else earning.default_amount ) /month_days-diff
                            else:
                                earning.amount = (earning.additional_amount if earning.additional_amount else earning.default_amount  * 0.5)/month_days-diff
                                gross = 0.5
                            basic_earnings.append(earning) 
                                                  
                else:
                    basic_earnings.append(earning)
                self.earnings = basic_earnings
        except Exception as err:
            print(err)
    self.gross_pay = (self.get_component_totals("earnings", depends_on_payment_days=1)) * gross

    self.base_gross_pay = flt(
        flt(self.gross_pay) * flt(self.exchange_rate), self.precision("base_gross_pay")
    )

    if self.salary_structure:
        self.calculate_component_amounts("deductions")

    set_loan_repayment(self)
    self.set_precision_for_component_amounts()
    self.set_net_pay()
    self.compute_income_tax_breakup()
    

def custom_calculate_component_amounts(self, component_type):
    if not getattr(self, "_salary_structure_doc", None):
        self._salary_structure_doc = frappe.get_doc("Salary Structure", self.salary_structure)

    self.add_structure_components(component_type)
    payroll_entry=frappe.get_doc("Payroll Entry",self.payroll_entry)
    if not payroll_entry.custom_payroll_type_ehc:
        self.add_additional_salary_components(component_type)
    
    if component_type == "earnings":
        self.add_employee_benefits()
    else:
        self.add_tax_components()


def override_validate(self):
    self.status = self.get_status()
    validate_active_employee(self.employee)
    self.validate_dates()
    self.check_existing()

    if not self.salary_slip_based_on_timesheet:
        self.get_date_details()

    if not (len(self.get("earnings")) or len(self.get("deductions"))):
        # get details from salary structure
        self.get_emp_and_working_day_details()
    else:
        custom_get_working_days_details(self, lwp=self.leave_without_pay)
        
    calculate_lfp(self)
    self.calculate_net_pay()
    self.compute_year_to_date()
    self.compute_month_to_date()
    self.compute_component_wise_year_to_date()
    self.add_leave_balances()
    self.compute_income_tax_breakup()

    if frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"):
        max_working_hours = frappe.db.get_single_value(
            "Payroll Settings", "max_working_hours_against_timesheet"
        )
        if self.salary_slip_based_on_timesheet and (self.total_working_hours > int(max_working_hours)):
            frappe.msgprint(
                _("Total working hours should not be greater than max working hours {0}").format(
                    max_working_hours
                ),
                alert=True,
            )

def calculate_lfp(self):
    check_deduction = frappe.db.get_all('Attendance Deduction',{'employee':self.employee, 'docstatus':1},['*'])
    if check_deduction:
        if self.docstatus == 0:
            try:
                days = 0
                for deduction in check_deduction:
                    start_month = get_datetime(self.start_date).month
                    end_month = get_datetime(self.end_date).month
                    deduction_month = month_name_to_number(deduction.month)
                    start_month <= deduction_month <= end_month
                    if len(deduction.fiscal_year) > 4:
                        f_year = int(((deduction.fiscal_year).split('-'))[0])
                    else:
                        f_year = int((deduction.fiscal_year))
                    if (start_month <= deduction_month <= end_month) and int(get_datetime(self.start_date).year) == f_year:
                        if deduction.deduction_hours:
                            standard_working_hours = frappe.db.get_single_value('HR Settings','standard_working_hours')
                            if standard_working_hours:
                                day = (deduction.deduction_hours)/standard_working_hours
                            else:
                                day = 0
                            days += day
                        if deduction.deduction_days:
                            day = deduction.deduction_days
                            days += day
                        elif deduction.penalty_days == 'Penalty Based':
                            day = deduction.penalty_days 
                            days += day                   
                    else:
                        pass
                
                self.leave_without_pay += days
                self.payment_days = self.payment_days - self.leave_without_pay
            except Exception as err:
                print(err)
                pass

def month_name_to_number(month_name):
    datetime_object = datetime.datetime.strptime(month_name, "%B")
    return datetime_object

def custom_get_working_days_details(self, joining_date=None, relieving_date=None, lwp=None, for_preview=0):
        payroll_settings = frappe.get_cached_value(
                        "Payroll Settings",
                        None,
                        (
                                "payroll_based_on",
                                "include_holidays_in_total_working_days",
                                "consider_marked_attendance_on_holidays",
                                "daily_wages_fraction_for_half_day",
                                "consider_unmarked_attendance_as",
                        ),
                        as_dict=1,
        )
        include_holidays_in_total_working_days = frappe.db.get_single_value(
            "Payroll Settings", "include_holidays_in_total_working_days"
        )

        consider_marked_attendance_on_holidays = (
                        payroll_settings.include_holidays_in_total_working_days
                        and payroll_settings.consider_marked_attendance_on_holidays
        )
        daily_wages_fraction_for_half_day = flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5
        working_days = date_diff(self.end_date, self.start_date) + 1
        if for_preview:
            self.total_working_days = working_days
            self.payment_days = working_days
            return
        holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
        working_days_list = [add_days(getdate(self.start_date), days=day) for day in range(0, working_days)]

        if not cint(include_holidays_in_total_working_days):
            working_days_list = [i for i in working_days_list if i not in holidays]

            working_days -= len(holidays)
            if working_days < 0:
                frappe.throw(_("There are more holidays than working days this month."))

        if not payroll_settings.payroll_based_on:
            frappe.throw(_("Please set Payroll based on in Payroll settings"))

        if payroll_settings.payroll_based_on == "Attendance":
            actual_lwp, absent = self.calculate_lwp_ppl_and_absent_days_based_on_attendance(
                holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
            )
            self.absent_days = absent
        else:
            actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(
                holidays, working_days_list, daily_wages_fraction_for_half_day
            )
        if not lwp:
            lwp = actual_lwp
        elif lwp != actual_lwp:
            pass
            # frappe.msgprint(
            #     _("Leave Without Pay does not match with approved {} records").format(payroll_based_on)
            # )

        self.leave_without_pay = lwp
        self.total_working_days = working_days

        payment_days = self.get_payment_days(
            payroll_settings.include_holidays_in_total_working_days
        )

        if flt(payment_days) > flt(lwp):
            self.payment_days = flt(payment_days) - flt(lwp)

            if payroll_settings.payroll_based_on == "Attendance":
                self.payment_days -= flt(absent)

            consider_unmarked_attendance_as = (
                frappe.db.get_value("Payroll Settings", {}, "consider_unmarked_attendance_as") or "Present"
            )
            if payroll_settings.payroll_based_on == "Attendance" and consider_unmarked_attendance_as == "Absent":
                unmarked_days = self.get_unmarked_days(payroll_settings.include_holidays_in_total_working_days, holidays)
                self.absent_days += unmarked_days  # will be treated as absent
                self.payment_days -= unmarked_days
        else:
            self.payment_days = 0
