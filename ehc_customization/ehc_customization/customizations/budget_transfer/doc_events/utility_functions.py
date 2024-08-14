import frappe
from frappe import _
from frappe.query_builder.functions import Sum, Count

@frappe.whitelist()
def filter_from_account(doctype=None, txt=None, searchfield=None, page_len=None, start=None, filters=None):
    txt = "%" + txt + "%"
    budget_account = frappe.qb.DocType('Budget Account')
    budget_account_data = (frappe.qb.from_(budget_account)
        .select(budget_account.account)
        .where(budget_account.parent == filters.get('from_budget'))
        .where(budget_account.account.like(txt))
    ).run(as_dict=False)
    return budget_account_data


@frappe.whitelist()
def filter_to_budget(doctype=None, txt=None, searchfield=None, page_len=None, start=None, filters=None):
    txt = "%" + txt + "%"
    budget = frappe.qb.DocType('Budget')
    budget__data = (frappe.qb.from_(budget)
        .select(budget.name)
        .where(budget.budget_against == filters.get('to_budget_against'))
        .where(budget.cost_center == filters.get('cost_center'))
        .where(budget.accounting_department == filters.get('accounting_department'))
        .where(budget.docstatus == filters.get('docstatus'))
        .where(budget.name.like(txt))
    ).run(as_dict=False)
    return budget__data


@frappe.whitelist()
def fetch_budget_before_transfer(account=None, parent=None, from_budget_against=None):
    try:
        if account and parent:
            resp = frappe.db.get_value('Budget Account', {'account': account, 'parent': parent}, [
                                       'custom_akd_budget_before_transfer', 'budget_amount'], as_dict=1)
            if from_budget_against == 'Cost Center':
                cost_center = frappe.db.get_value(
                    'Budget', parent, 'cost_center')
                gl_entry = frappe.qb.DocType('GL Entry')
                count = Sum(gl_entry.debit).as_("budget_available")
                budget_available = (frappe.qb.from_(gl_entry)
                    .select(count)
                    .where(gl_entry.account == account)
                    .where(gl_entry.cost_center == cost_center)
                    .where(gl_entry.fiscal_year == frappe.defaults.get_user_default("fiscal_year"))
                    .where(gl_entry.is_cancelled == 0)
                ).run(as_dict=True)
            budget_available = {
                'budget_available': budget_available[0]['budget_available']}
            resp.update(budget_available)
            return resp
    except Exception as e:
        frappe.log_error(frappe.get_traceback())


def update_budget_account(doc, method):
    print(doc)
    to_budget = doc.to_budget
    from_budget = doc.from_budget
    to_account = doc.to_account
    from_account = doc.from_account
    # to_budget
    name1 = frappe.get_list('Budget Account', filters={'parent': to_budget, 'account': to_account}, fields=[
                        'name', 'budget_amount', 'custom_akd_budget_received'],ignore_permissions=True)
    if name1:
        if doc.docstatus == 1:
            frappe.db.set_value('Budget Account', name1[0]['name'], {
                'custom_akd_budget_received': name1[0]['custom_akd_budget_received'] + doc.transfer,
                'budget_amount': name1[0]['budget_amount'] + doc.transfer
            })
        elif doc.docstatus == 2:
            frappe.db.set_value('Budget Account', name1[0]['name'], {
                'custom_akd_budget_received': name1[0]['custom_akd_budget_received'] - doc.transfer,
                'budget_amount': name1[0]['budget_amount'] - doc.transfer
            })
        # frappe.db.commit()

    # from_budget
    name2 = frappe.get_list('Budget Account', filters={'parent': from_budget, 'account': from_account}, fields=[
                               'name', 'budget_amount', 'custom_akd_transfer_amount'],ignore_permissions=True)
    if name2:
        if doc.docstatus == 1:
            frappe.db.set_value('Budget Account', name2[0]['name'], {
                'custom_akd_transfer_amount': name2[0]['custom_akd_transfer_amount'] + doc.transfer,
                'budget_amount': name2[0]['budget_amount'] - doc.transfer
            })
        elif doc.docstatus == 2:
            frappe.db.set_value('Budget Account', name2[0]['name'], {
                'custom_akd_transfer_amount': name2[0]['custom_akd_transfer_amount'] - doc.transfer,
                'budget_amount': name2[0]['budget_amount'] + doc.transfer
            })
        # frappe.db.commit()

    # update total_budget for to_budget and from_budget
    budget_list = []
    budget_list.append(to_budget)
    budget_list.append(from_budget)
    for budget in budget_list:
        total = 0
        budget_doc = frappe.get_doc("Budget", budget)
        for amount in budget_doc.accounts:
            total = total + amount.budget_amount
        frappe.db.set_value('Budget', budget, {'custom_akd_total_budget': total})
        # frappe.db.commit()