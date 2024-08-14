import json

import frappe


def update_roles_in_user(roles_list, user, uac):
	doc = frappe.get_doc("Users Access Control", uac)
	roles_list_data = json.loads(roles_list) if roles_list else []

	to_remove = [
		row
		for row in doc.roles_assigned
		if row.user == user and (not roles_list or row.role not in roles_list_data)
	]
	for row in to_remove:
		doc.remove(row)

	doc.save()
	return doc
