import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def get_late_details(employee, month):
	start_date, end_date = get_date_range(2024, month)
	get_count = len(frappe.db.get_all('Attendance', {'employee': employee,'attendance_date':('between', [start_date, end_date]),'late_entry':1}, ['late_entry']))
		
	return get_count


def get_date_range(year, month):
    month = datetime.strptime(month, '%B').month
    num_days = calendar.monthrange(year, month)[1]
    start_date = f'{year}-{month:02d}-01'
    end_date = f'{year}-{month:02d}-{num_days:02d}'

    return start_date, end_date	


@frappe.whitelist()
def update_permission(email, employee):
    try:
        if not frappe.db.exists('User Permission', {'user': email, 'allow': 'Employee', 'for_value': employee}):        
            new_doc = frappe.new_doc('User Permission')
            new_doc.user = email
            new_doc.allow = 'Employee'
            new_doc.for_value = employee
            new_doc.apply_to_all_doctypes = 0
            new_doc.applicable_for = 'Violation Request'
            new_doc.hide_descendants = 1
            new_doc.save()
    except:
        pass
	   
@frappe.whitelist()
def query_filter(user):
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("User is not an Linked Employee"))
    get_reports_to = frappe.db.get_list('Employee', {'reports_to': employee},pluck='name')
    employee = [employee] + get_reports_to
    return employee

@frappe.whitelist()
def query_filters(user):
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("User is not an Linked Employee"))
    get_reports_to = frappe.db.get_list('Employee', {'reports_to': employee},pluck='name')
    employee = get_reports_to
    return employee


@frappe.whitelist()
def deduction_mapping(source_name, target_doc=None):
    doc = get_mapped_doc(
        "Violation Request",
        source_name,
        {
            "Violation Request": {"doctype": "Attendance Deduction"},
        },
        target_doc,
    )

    return doc

def validate(doc, method=None):
    check_exists = frappe.db.get_all('Violation Request',{'employee':doc.employee, 'month':doc.month, 'fiscal_year':doc.fiscal_year, 'name':['!=', doc.name]})
    if check_exists:
         frappe.throw(_("Violation Request Already Exists for Specific Period"))

    if doc.status == 'Forward To HR':
        if not doc.hr_details:
            frappe.throw(_("HR Details Not Assigned for Employee"))

    if doc.status == 'Forward To Attendance Team':
        if not doc.attendance_team:
            frappe.throw(_("Attendance Team Details Not Assigned for Employee"))

 