// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Component History"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"hidden": 1

		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname": "salary_component",
			"label": __("Salary Component"),
			"fieldtype": "Link",
			"options": "Salary Component",
			"depends_on": "eval: !doc.scholarship",
			"width": "100px"
		},
		{
			"fieldname": "scholarship",
			"label": __("Scholarship Record"),
			"fieldtype": "Check",
			"default":0,
			"width": "100px"
		},

	]
};
