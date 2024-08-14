// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["EHC Organizational Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("company"),
		},
		{
			"fieldname":"employee",
			"label": ("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},

        {
			"fieldname":"designation",
			"label": ("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
		},
		{
			"fieldname":"department",
			"label": ("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname":"branch",
			"label": ("Network"),
			"fieldtype": "Link",
			"options": "Branch",
		},

	],
	"initial_depth":0,
	"formatter":function(value, row, column, data, default_formatter) {
		// console.log(value, row, column, data, default_formatter)
		return default_formatter(value, row, column, data)
	},
	onload: function (report) {
		report.page.add_inner_button(__("Chart View"), function () {
			frappe.set_route("EHC Organizational Chart");
		});
	},
};
