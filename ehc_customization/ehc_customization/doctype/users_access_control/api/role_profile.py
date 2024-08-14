import frappe
from frappe.query_builder import DocType


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def role_profile_query(doctype, txt, searchfield, start, page_len, filters):
	role_profile = DocType("Role Profile")
	user = filters["user"]
	# return frappe.db.sql(
	# 	"""
	#     SELECT name from `tabRole Profile`
	# 			WHERE modified_by = %s

	#     """,
	# 	(user,),
	# )
	return (
		frappe.qb.from_(role_profile)
		.select(role_profile.name)
		.where(role_profile.modified_by == user)
		.run()
	)
