import frappe
from frappe.query_builder.functions import Count


@frappe.whitelist()
def get_children(parent=None, company=None,designation=None,department=None,employee_name=None,branch=None,exclude_node=None):
	
	filters = [["status", "=", "Active"]]
	if company and company != "All Companies":
		filters.append(["company", "=", company])

	if parent and company and parent != company:
		filters.append(["reports_to", "=", parent])
	else:
		filters.append(["reports_to", "=", ""])

	if exclude_node:
		filters.append(["name", "!=", exclude_node])
	
	if designation:
		filters.append(["designation","=",designation])
	
	if department:
		filters.append(["department","=",department])
 
	if branch:
		filters.append(["branch","=",branch])
 
	if employee_name:
		filters.append(["name","=",employee_name])

	employees = frappe.get_all(
		"Employee",
		fields=[
			"employee_name as name",
			"name as id",
			"lft",
			"rgt",
			"reports_to",
			"image",
			"designation as title",
		],
		filters=filters,
		order_by="name",
	)

	for employee in employees:
		employee.connections = get_connections(employee.id, employee.lft, employee.rgt)
		employee.expandable = bool(employee.connections)

	return employees


def get_connections(employee: str, lft: int, rgt: int) -> int:
	Employee = frappe.qb.DocType("Employee")
	query = (
		frappe.qb.from_(Employee)
		.select(Count(Employee.name))
		.where((Employee.lft > lft) & (Employee.rgt < rgt) & (Employee.status == "Active"))
	).run()
	return query[0][0]


@frappe.whitelist()
def get_all_nodes(method, company,designation=None,department=None,employee_name=None,branch=None):
	"""Recursively gets all data from nodes"""
	method = frappe.get_attr(method)
	
	if method not in frappe.whitelisted:
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	root_nodes = method(company=company,designation=designation,department=department,employee_name=employee_name,branch=branch)
	result = []
	nodes_to_expand = []

	for root in root_nodes:
		data = method(root.id,company)
		result.append(dict(parent=root.id, parent_name=root.name, data=data))
		nodes_to_expand.extend(
			[{"id": d.get("id"), "name": d.get("name")} for d in data if d.get("expandable")]
		)

	while nodes_to_expand:
		parent = nodes_to_expand.pop(0)
		data = method(parent.get("id"),company)
		result.append(dict(parent=parent.get("id"), parent_name=parent.get("name"), data=data))
		for d in data:
			if d.get("expandable"):
				nodes_to_expand.append({"id": d.get("id"), "name": d.get("name")})

	return result



