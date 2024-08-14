// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["EHC Salary Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		},
		{
			"fieldname": "accounting_department",
			"label": __("Accounting Department"),
			"fieldtype": "MultiSelectList",
			"options": "Accounting Department",
			"width": "100px",
			get_data: function (txt) {
				return frappe.db.get_link_options("Accounting Department", txt, {
					company: frappe.query_report.get_filter_value("company"),
				});
			},
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "MultiSelectList",
			options: "Cost Center",
			get_data: function (txt) {
				return frappe.db.get_link_options("Cost Center", txt, {
					company: frappe.query_report.get_filter_value("company"),

				});
			},
		},
		{
			"fieldname":"financial_job_category",
			"label": __("Financial Job Category"),
			"fieldtype": "Select",
			"options": ["","Pharmacy","Physician","Allied Health","Nursing","Admin"],
			"width": "100px"
		},
		{
			"fieldname":"nationality_group",
			"label": __("Nationality Group"),
			"fieldtype": "Select",
			"options": ["","غيرسعودي" , "سعودي"],
			"width": "100px"
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": "100px"
		},
		{
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": "100px"
		},
		{
			"fieldname":"branch",
			"label": __("Network"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100px"
		},
		{
			"fieldname":"group_by_salary_component",
			"label": __("Group By Salary Component"),
			"fieldtype": "Check",
			"width": "100px"
		},
	]
}