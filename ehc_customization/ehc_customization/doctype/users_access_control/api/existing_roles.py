import frappe
from frappe.query_builder import DocType


@frappe.whitelist()
def get_existing_role(user, self):
	get_roles = DocType("Get Roles")
	user_doc = frappe.get_doc("Users Access Control", self)
	roles_list = frappe.db.get_all("Has Role", filters={"parent": user}, fields=["role"])
	user_role = []
	for row in roles_list:
		# role_exist = frappe.db.sql(
		# 	f""" select role from `tabGet Roles` where parent = '{self}'
		# 	and  role = '{row['role']}' """,
		# 	as_dict=1,
		# )
		role_exist = (
			frappe.qb.from_(get_roles)
			.select(get_roles.role)
			.where(get_roles.parent == self)
			.where(get_roles.role == row["role"])
			.run()
		)
		if not role_exist:
			user_doc.append("get_roles", {"role": row["role"], "user": frappe.session.user})

	user_doc.save()
	return user_doc
