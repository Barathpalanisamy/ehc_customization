# # Copyright (c) 2024, 8848digital and contributors
# # For license information, please see license.txt

# import json

import frappe
from frappe.model.document import Document

from ehc_customization.ehc_customization.doctype.users_access_control.api.role_query import roles
from ehc_customization.ehc_customization.doctype.users_access_control.api.roles_from_roles_profile import (
	get_role_against_role_profile,
)
from ehc_customization.ehc_customization.doctype.users_access_control.api.update_roles import (
	update_roles_in_user,
)
from ehc_customization.ehc_customization.doctype.users_access_control.doc_events.utility_functions import (
	set_roles_assigned,
	set_roles_from_role_profile,
	set_user,
	update_user,
)


class UsersAccessControl(Document):
	def validate(self, method=None):
		set_user(self)
		set_roles_assigned(self)
		set_roles_from_role_profile(self)
		update_user(self)


@frappe.whitelist()
def role_query(user, name):
	if user:
		user_role = frappe.db.get_all(
			"Roles Assigned", filters={"user": user, "parent": name}, fields=["role", "user"]
		)
		return user_role


@frappe.whitelist()
def get_role_from_role_profile(role_profile):
	get_role_against_role_profile(role_profile)


@frappe.whitelist()
def update_roles(roles_list, user, uac):
	update_roles_in_user(roles_list, user, uac)
