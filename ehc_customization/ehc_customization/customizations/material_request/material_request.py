import frappe
from erpnext.stock.get_item_details import get_company_total_stock
from frappe import _
from frappe.utils import flt

from ehc_customization.ehc_customization.customizations.material_request.api.available_qty import (
	get_avail_qty,
)
from ehc_customization.ehc_customization.customizations.material_request.doc_events.utility_functions import (
	validation_on_avail_qty,
)
from ehc_customization.ehc_customization.utility.budget_warnings import budget_warnings,create_or_update_entry_log,allow_validation


def validate(self, method=None):
	budget_warnings(self)
	allow_validation(self)
	validation_on_avail_qty(self)

def on_submit(self, method=None):
	if self.docstatus == 1:
		create_or_update_entry_log(self, method)

def after_save(self, method=None):
	create_or_update_entry_log(self, method)

def on_update(self, method=None):
	create_or_update_entry_log(self, method)

def on_cancel(self, method=None):
	create_or_update_entry_log(self, method)

@frappe.whitelist()
def get_available_qty(item_code, warehouse, company):
	return get_avail_qty(item_code, warehouse, company)
	
