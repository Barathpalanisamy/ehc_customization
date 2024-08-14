import frappe
from frappe.query_builder import DocType


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def user_role_query(doctype, txt, searchfield, start, page_len, filters):
	user_account_profile = DocType("User Account Profile")
	roles_assigned = DocType("Roles Assigned")
	get_roles = DocType("Roles Assigned")
	user = filters["user"]
	if user == "Administrator":
		# roles = frappe.db.sql(
		# 	"""
		# 	SELECT rp.profile
		# 		FROM `tabUser Account Profile` rp

		# 	"""
		# )
		roles = frappe.qb.from_(user_account_profile).select(user_account_profile.profile).where(user_account_profile.profile.like(f"%{txt}%")).run()
	else:
		# roles = frappe.db.sql(
		# 	"""
		# 	SELECT rp.profile
		# 		FROM `tabUser Account Profile` rp
		# 		LEFT JOIN `tabRoles Assigned` gr ON gr.role = rp.profile
		# 		WHERE gr.parent = %s
		# 		OR rp.parent_profile IN (
		# 			SELECT role
		# 			FROM `tabGet Roles`
		# 			WHERE parent = %s
		# 		)
		# 	""",
		# 	(user, user),
		# )

		r = frappe.qb.from_(get_roles).select(get_roles.role).where(get_roles.parent == user).run()
              
		roles = (
                   frappe.qb.from_(user_account_profile)
                   .left_join(roles_assigned)
                   .on(roles_assigned.role == user_account_profile.profile)
                   .select(user_account_profile.profile)
                   .where(
				((roles_assigned.parent == user) or (user_account_profile.parent_profile.isin(r)))
		  	    and (user_account_profile.name.like(f"%{txt}%"))
			)
			.run()
		)
		frappe.errprint(txt)

	return roles
