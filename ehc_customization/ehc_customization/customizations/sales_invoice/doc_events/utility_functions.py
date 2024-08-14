import frappe
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

def create_mode_of_payment(sales_invoice):
    if sales_invoice.custom_is_paid:
        total_payment_amount = sum([mode.amount for mode in sales_invoice.custom_payment_mode])
        check_excess_access = frappe.get_doc('Accounts Settings')
        if (total_payment_amount > sales_invoice.grand_total) and not check_excess_access.custom_allow_excess_payment:
            frappe.throw(_('Payment Amount Greater than Grand Total'))   
        calculate_unallocated_amount(sales_invoice)

def calculate_unallocated_amount(sales_invoice):
    journal_entry_accounts = []
    new_journal_entry = frappe.new_doc('Journal Entry')
    new_journal_entry.voucher_type = 'Journal Entry'
    new_journal_entry.company = sales_invoice.company
    new_journal_entry.posting_date = sales_invoice.posting_date
    new_journal_entry.custom_copayment = 'Yes'
    if sales_invoice.outstanding_amount >0:
        journal_entry_accounts.append(
            {
                'account': sales_invoice.debit_to,
                'party_type': 'Customer',
                'party': sales_invoice.customer,
                'cost_center': sales_invoice.cost_center,
                'accounting_department': sales_invoice.accounting_department,
                'debit_in_account_currency':0,
                'credit_in_account_currency': sales_invoice.custom_total_amount if sales_invoice.outstanding_amount > sales_invoice.custom_total_amount else sales_invoice.outstanding_amount,
                'reference_type': 'Sales Invoice',
                'reference_name': sales_invoice.name,
                'is_advance': 'No'
            }
        )
    reduced_last_row = sales_invoice.outstanding_amount
    if not sales_invoice.custom_payment_mode:
        frappe.throw(_('Payment Table Empty'))
    for idx, mode in enumerate(sales_invoice.custom_payment_mode):
        if mode.amount <= 0:
            frappe.throw(_('Payment Table Amount not valid. Enter valid Amount'))
        get_account = frappe.db.get_value('Mode of Payment Account',{'parent':mode.mode_of_payment, 'company':sales_invoice.company},['default_account'])
        if sales_invoice.total_advance and sales_invoice.outstanding_amount <=0 and idx ==0:
            journal_entry_accounts.append(
                {
                    'account': get_account,
                    'cost_center': sales_invoice.cost_center,
                    'accounting_department': sales_invoice.accounting_department,
                    'debit_in_account_currency':mode.amount,
                    'credit_in_account_currency':0,
                    'is_advance': 'No'
                }
            )
        else:
            journal_entry_accounts.append(
                {
                    'account': get_account,
                    'cost_center': sales_invoice.cost_center,
                    'accounting_department': sales_invoice.accounting_department,
                    'debit_in_account_currency':mode.amount,
                    'credit_in_account_currency':0,
                    'is_advance': 'No'
                }
            )
        reduced_last_row -= mode.amount
    if reduced_last_row < 0:
         journal_entry_accounts.append(
        {
            'account': sales_invoice.debit_to,
            'party_type': 'Customer',
            'party': sales_invoice.customer,
            'cost_center': sales_invoice.cost_center,
            'accounting_department': sales_invoice.accounting_department,
            'debit_in_account_currency':0,
            'credit_in_account_currency':abs(reduced_last_row),
            # 'reference_type': '',
            # 'reference_name': '',
            'is_advance': 'Yes'
        }
    )


    new_journal_entry.set("accounts", journal_entry_accounts)
    new_journal_entry.insert()
    new_journal_entry.submit()


def skip_validate_allocated_amount():
    pass

def set_missing_ref_details(force=True):
    pass

@frappe.whitelist()
def create_update_price_list(price_list_name):
    if not frappe.db.exists('Price List', price_list_name):
        create_price_list = frappe.new_doc('Price List')
        create_price_list.price_list_name = price_list_name
        create_price_list.selling = 1
        create_price_list.insert()
    return 1
