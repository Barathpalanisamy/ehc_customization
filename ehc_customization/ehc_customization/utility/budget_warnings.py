import frappe
from frappe import _
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.budget.budget import get_accumulated_monthly_budget,get_expense_breakup,get_requested_amount,get_ordered_amount
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import add_months, flt, fmt_money, get_last_day, getdate
from erpnext.controllers.subcontracting_controller import get_item_details
from ehc_customization.ehc_customization.utility.budget_calculation import validate_expense_against_budget
class BudgetError(frappe.ValidationError):
	pass

def allow_validation(doc):
    check_existing = frappe.db.get_list('Entry Log', {'doctype_name': doc.name},pluck = 'name')
    if check_existing:
        for val in check_existing:
            get_doc = frappe.get_doc('Entry Log', val)
            if doc.custom_budget_validation:
                get_doc.workflow_state = 1
            else:
                get_doc.workflow_state = 0
            get_doc.save()


def get_table_and_date(doctype):
    if doctype.doctype in ['Stock Entry', 'Stock Reconciliation']:
        table = doctype.items
    elif doctype.doctype == 'Journal Entry':
        table = doctype.accounts
    elif doctype.doctype == 'Expense Claim':
        table = doctype.expenses
    else:
        table = doctype.items
    date = (
        doctype.get('schedule_date') if doctype.get('schedule_date') 
        else doctype.get('due_date') if doctype.get('due_date') 
        else doctype.get('transaction_date') if doctype.get('transaction_date')
        else doctype.get('posting_date')
    ) 
    return table, date

def create_or_update_entry_log(doctype, method):
    table, date = get_table_and_date(doctype)
    update_existing = []
    for data in table:
        args = data.as_dict()
        if doctype.doctype == 'Journal Entry':
            args['amount'] = args['debit']
            args['expense_account'] = args['account']
        elif doctype.doctype == 'Stock Reconciliation':
            args.update({'cost_center': doctype.cost_center})
            args['accounting_department'] = doctype.accounting_department
            args['expense_account'] = doctype.expense_account
            args['amount'] = doctype.difference_amount
        elif doctype.doctype == 'Expense Claim':
            args['expense_account'] = args['default_account']

        if method in ['on_trash', 'on_submit']:
            entry_log = frappe.get_all('Entry Log', {'child_id': args['name']})
            if entry_log:
                entry_log = frappe.get_doc('Entry Log', {'child_id': args['name']})
                entry_log.delete()
        else:
            update_existing.append(args['name'])
            create_log(doctype, args, date)
            
    delete_missing_entry(doctype, update_existing)

def delete_missing_entry(doctype, update_existing):
    check_existing = frappe.db.get_list('Entry Log', {'doctype_name': doctype.name},pluck = 'child_id')
    if len(check_existing) != len(update_existing):
        missing_values = [value for value in check_existing if value not in update_existing]
        if missing_values:
            for name in missing_values:
                entry_log = frappe.get_all('Entry Log', {'child_id':name})
                if entry_log:
                    entry_log = frappe.get_doc('Entry Log', {'child_id': name})
                    entry_log.delete()

def create_log(doctype, args, date):
    if doctype.docstatus == 0:
        get_value = frappe.db.get_all('Entry Log', {'child_id': args['name']})
        if not get_value:
            entry_log = frappe.new_doc('Entry Log')
            entry_log.doctype_linked = doctype.doctype
            entry_log.child_id = args['name']
            entry_log.cost_center = args['cost_center']
            entry_log.accounting_department = args['accounting_department']
            entry_log.expense_account = args['expense_account']
            entry_log.amount = args['amount']
            entry_log.posting_date = date
            entry_log.company = doctype.company
            entry_log.doctype_name = doctype.name
            entry_log.is_cancel = 0
            entry_log.save()
        else:
            entry_log = frappe.get_doc('Entry Log', {'child_id':args['name']})
            entry_log.doctype_linked = doctype.doctype
            entry_log.child_id = args['name']
            entry_log.cost_center = args['cost_center']
            entry_log.accounting_department = args['accounting_department']
            entry_log.expense_account = args['expense_account']
            entry_log.amount = args['amount']
            entry_log.posting_date = date
            entry_log.company = doctype.company
            entry_log.doctype_name = doctype.name
            entry_log.is_cancel = 0
            entry_log.save()
    return

def budget_warnings(doctype):
    if doctype.doctype in ['Stock Entry', 'Stock Reconciliation']:
        table = doctype.items
    elif doctype.doctype == 'Journal Entry':
        table = doctype.accounts
    elif doctype.doctype == 'Expense Claim':
        table = doctype.expenses
    else:
        table = doctype.items
    date = (
        doctype.get('schedule_date') if doctype.get('schedule_date') 
        else doctype.get('due_date') if doctype.get('due_date') 
        else doctype.get('transaction_date') if doctype.get('transaction_date')
        else doctype.get('posting_date')
    )    
    prepare_args(doctype, table, date)

def prepare_args(doctype, table, date):
    for data in table:
        args = data.as_dict()
        if not args.accounting_department:
            args.accounting_department = ''
        if doctype.doctype == 'Expense Claim':
            get_account = frappe.get_doc('Expense Claim Account', {'parent':data.expense_type})
            args.update(
            {
                "doctype": doctype.doctype,
                "company": get_account.company,
                "expense_account": get_account.default_account,
                "posting_date": (
                    date
                ),
            }
            )
        elif doctype.doctype == 'Stock Reconciliation':
            args.update(
                {
                    "doctype": doctype.doctype,
                    "company": doctype.company,
                    "cost_center": doctype.cost_center,
                    "expense_account": doctype.expense_account,
                    "accounting_department": doctype.accounting_department,
                    "posting_date": (
                        date
                    ),
                }
            )
        else:
            args.update(
                {
                    "doctype": doctype.doctype,
                    "company": doctype.company,
                    "posting_date": (
                        date
                    ),
                }
            )
        validation(doctype, args, data)


def validation(doctype, args, data):
    if doctype.doctype == 'Journal Entry':
        amount = data.debit
    else:
        amount = data.amount
    permission = check_permission(args)
    if permission:
        validate_expense_against_budget(args, doctype, expense_amount=amount)


def check_permission(data):
    budget = frappe.qb.DocType('Budget')
    budget_account = frappe.qb.DocType('Budget Account')
    if data.get("cost_center") and data.get("accounting_department"):
        budget_data = (frappe.qb.from_(budget)
            .inner_join(budget_account)
            .on(budget.name == budget_account.parent)
            .select(budget.name)
            .where(budget.budget_against == 'Cost Center')
            .where(budget.cost_center == data.get("cost_center"))
            .where(budget.accounting_department == data.get("accounting_department"))
            .where(budget.company == data.get("company"))
            .where(budget.docstatus == 1)
        ).run(as_dict=True)
    elif data.get("cost_center") and not data.get("accounting_department"):
        budget_data = (frappe.qb.from_(budget)
                .inner_join(budget_account)
                .on(budget.name == budget_account.parent)
                .select(budget.name)
                .where(budget.budget_against == 'Cost Center')
                .where(budget.cost_center == data.get("cost_center"))
                .where(budget.company == data.get("company"))
                .where(budget.docstatus == 1)
            ).run(as_dict=True)
    else:
        budget_data = (frappe.qb.from_(budget)
                .inner_join(budget_account)
                .on(budget.name == budget_account.parent)
                .select(budget.name)
                .where(budget.budget_against == 'Cost Center')
                .where(budget.company == data.get("company"))
                .where(budget.docstatus == 1)
            ).run(as_dict=True)

    return budget_data

