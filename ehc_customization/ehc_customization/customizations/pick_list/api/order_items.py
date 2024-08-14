import frappe


def order_items_in_picklist(doc):
	self = frappe.get_doc("Pick List", doc)
	warehouse_list = list(set(ware.warehouse for ware in self.locations))

	if warehouse_list:

		warehouse_list.sort()

		parent_warehouse_dict = {
			ware: frappe.db.get_value("Warehouse", ware, "parent_warehouse") for ware in warehouse_list
		}

		parent_warehouse_list = sorted(set(parent_warehouse_dict.values()))

		warehouses = [
			ware for ware in warehouse_list if parent_warehouse_dict[ware] == parent_warehouse_list[0]
		]

		for war in parent_warehouse_list[1:]:
			warehouses.extend(ware for ware in warehouse_list if parent_warehouse_dict[ware] == war)

		self.locations.sort(key=lambda x: warehouses.index(x.warehouse))

	self.save()

	return self
