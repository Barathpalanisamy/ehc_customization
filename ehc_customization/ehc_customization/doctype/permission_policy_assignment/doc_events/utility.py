import frappe
from frappe import _

def validate(doc, method=None):
    check_exists = frappe.db.get_all('Permission Policy Assignment',{'employee':doc.employee,'fiscal_year':doc.fiscal_year, 'name':['!=', doc.name],'docstatus':['!=', 2]})
    if check_exists:
         frappe.throw(_("Permission Policy Assignment Already Exists for Specific Employee"))
