import frappe
from frappe import utils


def create_reserve_picklist(self):
	if self.material_request:
		for row in self.locations:
			if row.material_request_item:
				reserve_pl_exist = frappe.db.exists(
					"Reserve Pick List",
					{"voucher_no": self.name, "voucher_detail_no": row.material_request_item, "is_cancelled": 0},
				)
				if not reserve_pl_exist:
					reserve_pl = frappe.new_doc("Reserve Pick List")
					reserve_pl.item_code = row.item_code
					reserve_pl.warehouse = row.warehouse
					reserve_pl.stock_uom = row.stock_uom
					reserve_pl.company = self.company
					reserve_pl.reserved_qty = row.qty
					reserve_pl.voucher_type = "Pick List"
					reserve_pl.voucher_detail_no = row.material_request_item
					reserve_pl.posting_date = utils.today()
					reserve_pl.posting_time = utils.nowtime().split(".")[0]
					reserve_pl.is_cancelled = 0
					reserve_pl.insert()
					frappe.db.set_value("Reserve Pick List", reserve_pl.name, "voucher_no", self.name)
					frappe.db.set_value("Reserve Pick List", reserve_pl.name, "is_cancelled", 0)


def add_available_qty(self):
	if self.material_request:
		for row in self.locations:
			row.custom_available_qty = frappe.db.get_value(
				"Material Request Item", row.material_request_item, "custom_available_qty"
			)


def update_reserve_pick_list(self):
	if self.material_request:
		res_pl = frappe.db.get_all(
			"Reserve Pick List", filters={"voucher_no": "self.name"}, fields=["name"]
		)
		for row in res_pl:
			frappe.db.set_value("Reserve Pick List", row["name"], "is_cancelled", 1)
		# frappe.db.sql(
		# 	"""
		#             UPDATE `tabReserve Pick List`
		#             SET is_cancelled = 1
		#             WHERE voucher_no = %s
		#             """,
		# 	self.name,
		# )
