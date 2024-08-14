import frappe
from frappe import _

def update_employee_permission(employee):
    company_email = employee.get('company_email')
    generate_cost_center_permission = employee.get('custom_generate_cost_center_permission')
    generate_accounting_department_permission = employee.get('custom_generate_accounting_department_permission')
    cost_center = employee.get('payroll_cost_center')
    accounting_department = employee.get('ehc_accounting_department')
    invoice_type = employee.get('custom_invoice_type')
    if company_email:
        create_or_delete_user_permission(company_email, 'Cost Center', cost_center, generate_cost_center_permission)
        create_or_delete_user_permission(company_email, 'Accounting Department', accounting_department, generate_accounting_department_permission)
        if user_permission_exists(company_email, 'Invoice Type', invoice_type):
            remove_existing(company_email, 'Invoice Type')
        create_or_delete_user_permission(company_email, 'Invoice Type', invoice_type, True)
    else:
        frappe.throw(_('Company Mail Required'))
        
def user_permission_exists(user, allow, for_value):
    return frappe.db.exists('User Permission', {'user': user, 'allow': allow, 'for_value': for_value})

def create_or_delete_user_permission(user, allow, for_value, create_permission):
    if create_permission:
        if not frappe.db.exists('User Permission', {'user': user, 'allow': allow, 'for_value': for_value}) and for_value:
            remove_existing(user, allow)
            permission = frappe.new_doc('User Permission')
            permission.update({
                'user': user,
                'allow': allow,
                'for_value': for_value,
                'hide_descendants':1
            })
            permission.save()
        if not for_value:
            remove_existing(user, allow)

    else:
        remove_existing(user, allow)
    return

def remove_existing(user, allow):
    existing_doc = frappe.db.get_all('User Permission', {'user': user, 'allow': allow})
    if existing_doc:
        for i in existing_doc:
            frappe.delete_doc('User Permission', i.name)
            # frappe.clear_cache()
    return