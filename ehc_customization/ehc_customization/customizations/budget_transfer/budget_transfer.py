import frappe

from ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions import update_budget_account

def on_submit(self, method=None):
	update_budget_account(self, method)
	
def on_cancel(self, method=None):
	print('incoming')
	update_budget_account(self, method)
