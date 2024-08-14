# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import datetime
from erpnext.accounts.report.budget_variance_report.budget_variance_report import get_cost_centers
from erpnext.accounts.report.budget_variance_report.budget_variance_report import get_chart_data, get_fiscal_years, get_target_distribution_details
import frappe
from frappe import _
from frappe.utils import flt, formatdate
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	if filters.get("budget_against_filter"):
		dimensions = filters.get("budget_against_filter")
	else:
		dimensions = get_cost_centers(filters)

	period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
	cam_map, budget_details = get_dimension_account_month_map(filters)

	data = []
	for dimension in dimensions:
		dimension_items = cam_map.get(dimension)
		if dimension_items:
			budget_detail = [budget for budget in budget_details if budget.get('budget_against') == dimension]
			data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, budget_detail, 0)


	chart = get_chart_data(filters, columns, data)
	if filters.get("summary"):
		summary_filter = filters.get("summary")
		if summary_filter == "Cost Center":
			data = aggregate_data(data, 0)
			for row in data:
				del row[1]
				del row[1]

		elif summary_filter == "Account":
			data = aggregate_data(data, 1)
			for row in data:
				del row[0]
				del row[1]

		elif summary_filter == "Accounting Department":
			data = aggregate_data(data, 2)
			for row in data:
				del row[0]
				del row[0]

	return columns, data, None, chart

def aggregate_data(data,index):
	summary_data = {}
	for row in data:
		key = row[index]  

		if key not in summary_data:
			summary_data[key] = row[:3] + [0] * (len(row) - 3) 
		for i in range(3, len(row)):
			summary_data[key][i] += row[i]
	return [values for values in summary_data.values()]

def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, budget_detail, DCC_allocation):


	for account, monthwise_data in dimension_items.items():
		for accounting_department, budget_data in monthwise_data.items():
			row = [dimension, accounting_department, account]
			totals = [0, 0, 0]
			for year in get_fiscal_years(filters):
				last_total = 0
				for relevant_months in period_month_ranges:
					period_data = [0, 0, 0]
					for month in relevant_months:
						if budget_data.get(year[0]):
							month_data = budget_data.get(year[0]).get(month, {})
							for i, fieldname in enumerate(["target", "actual", "variance"]):
								value = flt(month_data.get(fieldname))
								period_data[i] += value
								totals[i] += value

					period_data[0] += last_total

					if DCC_allocation:
						period_data[0] = period_data[0] * (DCC_allocation / 100)
						period_data[1] = period_data[1] * (DCC_allocation / 100)

					if filters.get("show_cumulative"):
						last_total = period_data[0] - period_data[1]

					period_data[2] = period_data[0] - period_data[1]
					row += period_data
					if filters["period"] == "Yearly":
						value = [
							[i['custom_akd_budget_before_transfer'], i['custom_akd_transfer_amount'], i['custom_akd_budget_received']]
							for i in budget_detail
							if i['account'] == row[1] and i['budget_against'] == row[0] and i['fiscal_year'] == year[0] and i['accounting_department'] == row[2]
						]					
						if value:	
							total = value[0]		
						else:
							total = [0,0,0]
						row += total
			totals[2] = totals[0] - totals[1]
			if filters["period"] != "Yearly":
				row += totals
				unique_list_of_dicts = []
				for d in budget_detail:
					if d not in unique_list_of_dicts:
						unique_list_of_dicts.append(d)
				
				try:
					total = [0,0,0]
					for i in unique_list_of_dicts:
						if i['account'] == row[1] and i['accounting_department'] == row[2]:
							total[0]+= i['custom_akd_budget_before_transfer']
							total[1]+= (i['custom_akd_transfer_amount'])
							total[2]+= i['custom_akd_budget_received']					
				except:
					total = [0,0,0]
				row += total
			data.append(row)

	return data

def get_dimension_target_details(filters):

	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""
	if filters.get("budget_against_filter"):
		cond += """ and b.{budget_against} in (%s)""".format(budget_against=budget_against) % ", ".join(
			["%s"] * len(filters.get("budget_against_filter"))
		)
	
	if not filters.get("accounting_department"):

		budget_records = frappe.get_all(
			"Budget",
			filters={
				"docstatus": 1,
				"fiscal_year": ["between", (filters.from_fiscal_year, filters.to_fiscal_year)],
				"budget_against": filters.budget_against,
				"company": filters.company,
			},
			fields=["name", budget_against, "accounting_department", "monthly_distribution", "fiscal_year"]
		)

		budget_account_records = frappe.get_all(
			"Budget Account",
			filters={"parent": ["in", [br["name"] for br in budget_records]]},

			fields=["parent", "account", "budget_amount","custom_akd_budget_received","custom_akd_transfer_amount","custom_akd_budget_before_transfer"]

		)

	else:
		budget_records = frappe.get_all(
		"Budget",
		filters={
			"docstatus": 1,
			"fiscal_year": ["between", (filters.from_fiscal_year, filters.to_fiscal_year)],
			"budget_against": filters.budget_against,
			"accounting_department": ['In',filters.accounting_department],
			"company": filters.company,
		},
		
		fields=["name", budget_against, "accounting_department", "monthly_distribution", "fiscal_year"])
		budget_account_records = frappe.get_all(
			"Budget Account",
			filters={"parent": ["in", [br["name"] for br in budget_records]]},

			fields=["parent", "account", "budget_amount","custom_akd_budget_received","custom_akd_transfer_amount","custom_akd_budget_before_transfer"]

		)

		
	result = []
	for budget_record in budget_records:
		for budget_account_record in budget_account_records:
			if budget_record["name"] == budget_account_record["parent"]:
				result.append({
					"budget_against": budget_record[budget_against],
					"accounting_department": budget_record["accounting_department"],
					"monthly_distribution": budget_record["monthly_distribution"],
					"account": budget_account_record["account"],
					"budget_amount": budget_account_record["budget_amount"],

					"fiscal_year": budget_record["fiscal_year"],
					"custom_akd_transfer_amount":budget_account_record["custom_akd_transfer_amount"],
					"custom_akd_budget_received": budget_account_record["custom_akd_budget_received"],
					"custom_akd_budget_before_transfer": budget_account_record["custom_akd_budget_before_transfer"]

				})
	return result



def get_columns(filters):
	columns =[]
	if filters.get("summary") == "Cost Center":
		columns += [
			{
				"label": _(filters.get("budget_against")),
				"fieldtype": "Link",
				"fieldname": "budget_against",
				"options": filters.get("budget_against"),
				"width": 150,
			},    
		]
	elif filters.get("summary") == "Accounting Department":
		columns += [
			{
				"label": _("Accounting Department"),
				"fieldname": "accounting_department",
				"fieldtype": "Data",
				"width": 150,
			},      
		]
	elif filters.get("summary") == "Account":
		columns += [
			{
				"label": _("Account"),
				"fieldname": "Account",
				"fieldtype": "Link",
				"options": "Account",
				"width": 150,
			},      
		]
	else:
		columns += [
			{
				"label": _(filters.get("budget_against")),
				"fieldtype": "Link",
				"fieldname": "budget_against",
				"options": filters.get("budget_against"),
				"width": 150,
			},
			{
				"label": _("Account"),
				"fieldname": "Account",
				"fieldtype": "Link",
				"options": "Account",
				"width": 150,
			}, 
			{
				"label": _("Accounting Department"),
				"fieldname": "accounting_department",
				"fieldtype": "Data",
				"width": 150,
			},      
		]

	group_months = False if filters["period"] == "Monthly" else True

	fiscal_year = get_fiscal_years(filters)

	for year in fiscal_year:
		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
			if filters["period"] == "Yearly":
				labels = [
					_("Budget") + " " + str(year[0]),
					_("Actual") + " " + str(year[0]),
					_("Variance") + " " + str(year[0]),

					_("Budget Before Transfer")  + " " + str(year[0]),
							  _("Transfer Amount")  + " " + str(year[0]),
							  _("Received Amount") + " " + str(year[0]),

				]
				for label in labels:
					columns.append(
						{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
					)
			else:
				for label in [
					_("Budget") + " (%s)" + " " + str(year[0]),
					_("Actual") + " (%s)" + " " + str(year[0]),
					_("Variance") + " (%s)" + " " + str(year[0]),
				]:
					if group_months:
						label = (
							label
							% (
								formatdate(from_date, format_string="MMM")
								+ "-"
								+ formatdate(to_date, format_string="MMM")
							)
						)
					else:
						label = label % formatdate(from_date, format_string="MMM")

					columns.append(
						{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
					)

	if filters["period"] != "Yearly":

		for label in [_("Total Budget"), _("Total Actual"), _("Total Variance"),_("Budget Before Transfer"), _("Transfer Amount"), _("Received Amount")]:

			columns.append(
				{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
			)

	return columns


def get_dimension_account_month_map(filters):
	dimension_target_details = get_dimension_target_details(filters)
	tdd = get_target_distribution_details(filters)
	cam_map = {}

	get_budget_detail = []
	for ccd in dimension_target_details:
		actual_details = get_actual_details(ccd["budget_against"], filters)
		get_budget_details = {}

		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime("%B")
			cam_map.setdefault(ccd["budget_against"], {}).setdefault(ccd["accounting_department"], {}).setdefault(
				ccd["account"], {}
			).setdefault(ccd["fiscal_year"], {}).setdefault(month, frappe._dict({"target": 0.0, "actual": 0.0}))

			tav_dict = cam_map[ccd["budget_against"]][ccd["accounting_department"]][ccd["account"]][ccd["fiscal_year"]][month]
			month_percentage = (
				tdd.get(ccd["monthly_distribution"], {}).get(month, 0) if ccd["monthly_distribution"] else 100.0 / 12
			)

			tav_dict.target = flt(ccd["budget_amount"]) * month_percentage / 100

			for ad in actual_details.get(ccd["account"], []):
				if ad["posting_date"].month == month_id and ad["fiscal_year"] == ccd["fiscal_year"] and (ad["accounting_department"] or "") == (ccd["accounting_department"] or ''):
					tav_dict.actual += flt(ad["debit"]) - flt(ad["credit"])

			
			get_budget_details['budget_against'] = ccd['budget_against']
			get_budget_details['accounting_department'] = ccd['accounting_department']
			get_budget_details['account'] = ccd['account']
			get_budget_details['fiscal_year'] = ccd['fiscal_year']
			get_budget_details['custom_akd_transfer_amount'] = ccd['custom_akd_transfer_amount']
			get_budget_details['custom_akd_budget_received'] = ccd['custom_akd_budget_received']
			get_budget_details['custom_akd_budget_before_transfer'] = ccd['custom_akd_budget_before_transfer']
			get_budget_detail.append(get_budget_details)

	return cam_map, get_budget_detail
def get_actual_details(name, filters):
	budget_against = frappe.scrub(filters.get("budget_against"))
	cond = ""

	if filters.get("budget_against") == "Cost Center":
		cc_lft, cc_rgt = frappe.db.get_value("Cost Center", name, ["lft", "rgt"])
		cond = {
			"lft": cc_lft,
			"rgt": cc_rgt
		}

	gl_entries = frappe.get_all("GL Entry", filters={
		"posting_date": ["between", [filters.from_fiscal_year_start, filters.to_fiscal_year_end]],"cost_center":name
	}, fields=["account", "debit", "credit", "fiscal_year", "accounting_department", "posting_date",'name','cost_center'])

	budget_entries = frappe.get_all("Budget", filters={
		"docstatus": 1,
		budget_against: name
	}, fields=["name", budget_against])

	budget_accounts = {}
	for budget_entry in budget_entries:
		ba = frappe.get_all("Budget Account", filters={"parent": budget_entry.name}, fields=["account"])
		for account in ba:
			budget_accounts[account.account] = budget_entry[budget_against]

	cc_actual_details = {}
	for entry in gl_entries:
		account = entry["account"]
		if account in budget_accounts:
			entry["budget_against"] = budget_accounts[account]
			cc_actual_details.setdefault(account, []).append(entry)

	return cc_actual_details




def get_chart_data(filters, columns, data):
	if not data:
		return None

	labels = []
	fiscal_year = get_fiscal_years(filters)
	group_months = False if filters["period"] == "Monthly" else True

	for year in fiscal_year:
		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
			if filters["period"] == "Yearly":
				labels.append(str(year[0]))
			else:
				if group_months:
					label = (
						formatdate(from_date, format_string="MMM")
						+ "-"
						+ formatdate(to_date, format_string="MMM")
					)
					labels.append(label)
				else:
					label = formatdate(from_date, format_string="MMM")
					labels.append(label)

	no_of_columns = len(labels)

	budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns
	for d in data:
		values = d[2:]
		index = 0

		for i in range(no_of_columns):
			budget_values[i] += flt(values[index])
			actual_values[i] += flt(values[index + 1])
			index += 3

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Budget"), "chartType": "bar", "values": budget_values},
				{"name": _("Actual Expense"), "chartType": "bar", "values": actual_values},
			],
		},
		"type": "bar",

	}
