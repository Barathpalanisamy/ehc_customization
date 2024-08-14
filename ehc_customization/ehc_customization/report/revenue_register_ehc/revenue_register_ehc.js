// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Revenue Register EHC"] = {
	"filters": [
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
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"hidden": 1
		},
		{
			"fieldname": "mode_of_payment",
			"label": __("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"hidden": 1
		},
		{
			"fieldname": "owner",
			"label": __("Owner"),
			"fieldtype": "Link",
			"options": "User",
			"hidden": 1
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "MultiSelectList",
			"options": "Cost Center",
			get_data: function (txt) {
				return frappe.db.get_link_options("Cost Center", txt, {
					company: frappe.query_report.get_filter_value("company"),
					is_group: 0

				});
			},
		},
		{
			"fieldname": "accounting_department",
			"label": __("Accounting Department"),
			"fieldtype": "MultiSelectList",
			"options": "Accounting Department",
			get_data: function (txt) {
				return frappe.db.get_link_options("Accounting Department", txt, {
					company: frappe.query_report.get_filter_value("company"),
				});
			},
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"hidden": 1
		},
		{
			"fieldname": "ehc_invoice_type",
			"label": __("Invoice Type"),
			"fieldtype": "Select",
			"options": ["", "Outpatient", "Inpatient", "Emergency", "Investment", "Course"]
		},
		{
			"fieldname": "revenue_type",
			"label": __("Revenue Type"),
			"fieldtype": "Select",
			"options": ["", "Patient", "Investment", "Course"]
		},
		{
			"fieldname": "summary",
			"label": __("Summary Based on"),
			"fieldtype": "Select",
			"options": ["", "Invoice Type", "Revenue Type"]
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"hidden": 1
		}
	]
}

// Please remove Santosh from below line
erpnext.utils.add_dimensions('Santosh Revenue Register', 7);

