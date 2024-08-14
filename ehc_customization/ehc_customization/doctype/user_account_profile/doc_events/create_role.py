import frappe


def create_roles(self):
	if frappe.db.exists("Role", self.profile):
		pass
	else:
		user_role = frappe.new_doc("Role")
		user_role.role_name = self.profile
		user_role.save()
