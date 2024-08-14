import frappe


def get_role_against_role_profile(role_profile):
	roles_list = frappe.db.get_all("Has Role", filters={"parent": role_profile}, fields=["role"])
	return roles_list
