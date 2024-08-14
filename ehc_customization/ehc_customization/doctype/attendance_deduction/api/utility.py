import frappe
from frappe import _

def validate(doc, method=None):
    check_previous = frappe.db.get_all('Attendance Deduction', {
        'employee': doc.employee,
        'docstatus': ["!=", 2], 
        'name': ["!=", doc.name],
        'month': doc.month,
        'fiscal_year': doc.fiscal_year
    })
    if check_previous:
        frappe.throw(_("There is already an active entry. Please cancel it first."))
