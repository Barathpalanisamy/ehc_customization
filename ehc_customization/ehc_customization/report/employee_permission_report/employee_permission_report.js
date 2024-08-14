// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Permission Report"] = {
	"filters": [
		{
			"fieldname":"employee_name",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("All") },
				{ "value": 1, "label": __("Jan") },
				{ "value": 2, "label": __("Feb") },
				{ "value": 3, "label": __("Mar") },
				{ "value": 4, "label": __("Apr") },
				{ "value": 5, "label": __("May") },
				{ "value": 6, "label": __("June") },
				{ "value": 7, "label": __("July") },
				{ "value": 8, "label": __("Aug") },
				{ "value": 9, "label": __("Sep") },
				{ "value": 10, "label": __("Oct") },
				{ "value": 11, "label": __("Nov") },
				{ "value": 12, "label": __("Dec") },
			],
			"width": "100px"
		},
		{
			"fieldname":"time_interval",
			"label": __("Time Interval"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("All") },
				{ "value": "monthly", "label": __("Monthly") },
				{ "value": "daily", "label": __("Daily") },
				{ "value": "annual", "label": __("Annual") },
			],
			"width": "100px",
		},


	]
};