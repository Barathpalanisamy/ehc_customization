import frappe


def roles(user, name):
	if user:
		user_role = frappe.db.get_all(
			"Roles Assigned", filters={"user": user, "parent": name}, fields=["role", "user"], as_dict=1
		)
		return user_role
