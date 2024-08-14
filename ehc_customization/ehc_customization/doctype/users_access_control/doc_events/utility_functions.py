import frappe
from frappe.query_builder import DocType

from ehc_customization.ehc_customization.doctype.users_access_control.users_access_control import (
	get_role_against_role_profile,
)


def update_user(self):
	if not self.doc_created_by_user:
		user = frappe.get_doc("User", self.name)
		user.roles = []
		for row in self.roles_assigned:
			user.append("roles", {"role": row.role})
		user.save()


def set_user(self):
	for row in self.get_roles:
		if not row.user:
			row.user = frappe.session.user


def set_roles_assigned(self):
	RolesAssigned = DocType("Roles Assigned")
	if self.get_roles:
		roles_to_assign = []
		for row in self.get_roles:
			role_exist = (
				frappe.qb.from_(RolesAssigned)
				.select(RolesAssigned.role, RolesAssigned.parent)
				.where((RolesAssigned.parent == self.user) & (RolesAssigned.role == row.role))
				.run(as_dict=True)
			)
			if not role_exist:
				roles_to_assign.append({"role": row.role, "user": frappe.session.user})

		self.extend("roles_assigned", roles_to_assign)
	self.get_roles = []


def set_roles_from_role_profile(self):
	if self.role_profile:
		roles_list = get_role_against_role_profile(self.role_profile)
		if roles_list:
			for roles in roles_list:
				self.append("get_roles", {"role": roles["role"], "user": frappe.session.user})
	self.role_profile = ""
	set_roles_assigned(self)
