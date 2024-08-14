import frappe
import json

@frappe.whitelist()
def get_budget_accounts(budget):
    return frappe.db.get_all('Budget Account', filters={'parent': budget}, fields=['account', 'budget_amount'])

@frappe.whitelist()
def update_budget_accounts(budget, accounts):
    accounts = json.loads(accounts)
    try:
        total_base_budget = 0
        total_budget = 0
        for account in accounts:
            existing_account = frappe.get_value('Budget Account', {'parent': budget, 'account': account['account_name']}, 'name')
            
            if existing_account:
                # Update existing budget account
                budget_account_doc = frappe.get_doc('Budget Account', existing_account)
                old_amount = budget_account_doc.budget_amount
                budget_account_doc.custom_akd_budget_before_transfer = (account['account_value'] - budget_account_doc.budget_amount) + budget_account_doc.custom_akd_budget_before_transfer
                budget_account_doc.budget_amount = account['account_value']
                budget_account_doc.flags.ignore_validate_update_after_submit = True
                budget_account_doc.save()
                total_base_budget += budget_account_doc.custom_akd_budget_before_transfer
                total_budget += account['account_value']
                frappe.db.set_value('Budget', budget, 'custom_editable_budget',1)
                if old_amount != account['account_value']:
                    create_budget_log = frappe.new_doc('Budget Log')
                    create_budget_log.account = account['account_name']
                    create_budget_log.budget = budget
                    create_budget_log.amount_before_transfer = old_amount
                    create_budget_log.amount_after_transfer = account['account_value']
                    create_budget_log.difference_amount = (account['account_value'] - old_amount)
                    create_budget_log.user = frappe.session.user
                    create_budget_log.save()


            else:
                # Insert new budget account
                frappe.get_doc({
                    'doctype': 'Budget Account',
                    'budget': budget,
                    'account': account['account_name'],
                    'budget_amount': account['account_value'],
                    'parent':budget,
                    'parentfield':'accounts',
                    'parenttype':'Budget'
                }).insert()
        frappe.db.set_value('Budget', budget, 'custom_akd_total_base_budget',total_base_budget)
        frappe.db.set_value('Budget', budget, 'custom_akd_total_budget',total_budget)

        frappe.db.commit()
        return 'success'
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Budget Account Update Failed')
        return 'failed'