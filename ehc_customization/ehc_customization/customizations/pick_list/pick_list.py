import frappe

from ehc_customization.ehc_customization.customizations.pick_list.api.order_items import (
	order_items_in_picklist,
)
from ehc_customization.ehc_customization.customizations.pick_list.doc_events.utility_function import (
	add_available_qty,
	create_reserve_picklist,
	update_reserve_pick_list,
)


def validate(self, method=None):
	create_reserve_picklist(self)
	add_available_qty(self)


def on_cancel(self, method=None):
	update_reserve_pick_list(self)


@frappe.whitelist()
def order_items_as_per_warehouse(doc):
	order_items_in_picklist(doc)
