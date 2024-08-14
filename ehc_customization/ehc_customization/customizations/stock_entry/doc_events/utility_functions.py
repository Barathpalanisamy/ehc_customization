import frappe


def update_reserve_pl(self, skip_rpl_value):
	if self.pick_list:
		item_codes = [row.material_request_item for row in self.items]
		for item_code in item_codes:
			frappe.db.set_value(
				"Reserve Pick List", {"voucher_detail_no": item_code}, "skip_rpl", skip_rpl_value
			)
