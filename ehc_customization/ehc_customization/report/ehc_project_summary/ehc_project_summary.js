// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["EHC Project Summary"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "is_active",
			label: __("Is Active"),
			fieldtype: "Select",
			options: "\nYes\nNo",
			default: "Yes",
		},
        {
			fieldname: "name",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nOpen\nCompleted\nCancelled",
		},
		{
			fieldname: "project_type",
			label: __("Project Type"),
			fieldtype: "Link",
			options: "Project Type",
		},
		{
			fieldname: "priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: "\nLow\nMedium\nHigh",
		},
	],
};
