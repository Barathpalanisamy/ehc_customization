import frappe

@frappe.whitelist()
def get_accounting_departments(doctype, txt, searchfield, start, page_len, filters):
    cost_center = filters.get('cost_center')
    get_accounting_name = frappe.db.get_all('Accounting Department CC', {'parent':cost_center,'is_group':0}, ['accounting_department'])
    return [(dep['accounting_department'],) for dep in get_accounting_name]


@frappe.whitelist()
def multiple_account():
    get_account_settings  = frappe.get_doc('Accounts Settings')
    return get_account_settings.custom_allow_multiple_discount