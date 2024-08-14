import frappe
from erpnext.stock.get_item_details import get_company_total_stock
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_avail_qty(item_code, warehouse, company):
	bin_details = {"projected_qty": 0, "custom_available_qty": 0, "reserved_qty": 0}

	if warehouse:
		from frappe.query_builder.functions import Coalesce, Sum

		warehouses = get_warehouses(warehouse)
		bin = frappe.qb.DocType("Bin")
		bin_details = (
			frappe.qb.from_(bin)
			.select(
				Coalesce(Sum(bin.projected_qty), 0).as_("projected_qty"),
				Coalesce(Sum(bin.actual_qty), 0).as_("custom_available_qty"),
				Coalesce(Sum(bin.reserved_qty), 0).as_("reserved_qty"),
			)
			.where((bin.item_code == item_code) & (bin.warehouse.isin(warehouses)))
		).run(as_dict=True)[0]
		reserve_pl = frappe.qb.DocType("Reserve Pick List")
		reserve_pl_details = (
			frappe.qb.from_(reserve_pl)
			.select(
				Coalesce(Sum(reserve_pl.reserved_qty), 0).as_("reserve_qty"),
			)
			.where(
				(reserve_pl.item_code == item_code)
				& (reserve_pl.warehouse.isin(warehouses))
				& (reserve_pl.is_cancelled == 0)
				& (reserve_pl.skip_rpl == 0)
			)
		).run(as_dict=True)[0]

		if reserve_pl_details:
			bin_details["custom_available_qty"] -= reserve_pl_details["reserve_qty"]
	if company:
		bin_details["company_total_stock"] = get_company_total_stock(item_code, company)

	return bin_details


def get_warehouses(warehouse):
	warehouses = [warehouse]

	def get_child_warehouses(parent_warehouse):
		child_warehouses = []
		warehouse_list = frappe.db.get_all(
			"Warehouse", filters={"parent_warehouse": parent_warehouse}, fields=["name"]
		)
		for warehouse in warehouse_list:
			child_warehouses.append(warehouse["name"])
			if frappe.db.get_value("Warehouse", warehouse["name"], "is_group"):
				child_warehouses.extend(get_child_warehouses(warehouse["name"]))
		return child_warehouses

	if frappe.db.get_value("Warehouse", warehouse, "is_group"):
		warehouses.extend(get_child_warehouses(warehouse))

	return warehouses
