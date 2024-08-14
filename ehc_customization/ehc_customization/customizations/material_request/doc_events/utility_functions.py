import frappe
from frappe import _
from frappe.utils import flt

from ehc_customization.ehc_customization.customizations.material_request.api.available_qty import (
	get_avail_qty,
)


def validation_on_avail_qty(self):
	if self.material_request_type == "Material Transfer":
		for row in self.items:
			avail_qty = get_avail_qty(row.item_code, row.from_warehouse, self.company)
			if avail_qty["custom_available_qty"]:
				row.custom_available_qty = avail_qty["custom_available_qty"]
			if flt(avail_qty["custom_available_qty"]) == 0:
				frappe.msgprint(_("Zero Stock available for item {0}").format(row.item_code))
