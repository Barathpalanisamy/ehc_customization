import frappe

from ehc_customization.ehc_customization.customizations.stock_entry.doc_events.utility_functions import (
	update_reserve_pl,
)
from ehc_customization.ehc_customization.utility.budget_warnings import budget_warnings, create_or_update_entry_log, allow_validation


def on_submit(self, method=None):
	update_reserve_pl(self, 1)
	if self.docstatus == 1:
		create_or_update_entry_log(self, method)

def on_cancel(self, method=None):
	update_reserve_pl(self, 0)

def validate(self, method=None):
	budget_warnings(self)
	allow_validation(self)

def after_save(self, method=None):
	create_or_update_entry_log(self, method)

def on_update(self, method=None):
	create_or_update_entry_log(self, method)

def on_cancel(self, method=None):
	create_or_update_entry_log(self, method)



