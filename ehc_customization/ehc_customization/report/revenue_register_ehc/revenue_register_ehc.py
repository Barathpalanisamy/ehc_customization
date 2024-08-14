import frappe
from frappe import _, msgprint
from frappe.model.meta import get_field_precision
from frappe.utils import flt
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import flt, getdate
from pypika import Order
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimension_with_children,
)
from erpnext.accounts.report.utils import (
	apply_common_conditions
)
from erpnext.accounts.report.sales_register.sales_register import(
	get_mode_of_payments,
	get_invoice_cc_wh_map,
	get_invoice_so_dn_map,
	get_invoice_tax_map,
	get_internal_invoice_map,
	get_invoice_income_map
)
def execute(filters=None):
	return _execute(filters)


def _execute(filters, additional_table_columns=None, additional_query_columns=None):
	data = []

	if not filters:
		filters = frappe._dict({})
	if filters.get("summary") == 'Invoice Type':
		invoice_list = get_invoices(filters, additional_query_columns)
		columns, income_accounts, tax_accounts, unrealized_profit_loss_accounts = get_columns(filters,
			invoice_list, additional_table_columns
		)
		if not invoice_list:
			return columns, invoice_list
		grouped_invoices = {}
		company_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")
		invoice_income_map = get_invoice_income_map(invoice_list)
		invoice_income_map, invoice_tax_map = get_invoice_tax_map(
			invoice_list, invoice_income_map, income_accounts
		)
		for invoice in invoice_list:
			invoice_type = invoice.get("ehc_invoice_type")
			if invoice_type not in grouped_invoices:
				grouped_invoices[invoice_type] = {
				"net_total": 0,
				"tax_total": 0,
				"grand_total": 0,
				"outstanding_total": 0,
			}
			# net total
				
			base_net_total = 0
			for income_acc in income_accounts:
				if invoice.is_internal_customer and invoice.company == invoice.represents_company:
					income_amount = 0
				else:
					income_amount = flt(invoice_income_map.get(invoice.name, {}).get(income_acc))

				base_net_total += income_amount

			# tax amount
			total_tax = 0
			for tax_acc in tax_accounts:
				if tax_acc not in income_accounts:
					tax_amount_precision = (
					get_field_precision(
					frappe.get_meta("Sales Taxes and Charges").get_field("tax_amount"), currency=company_currency
					)
					or 2
				)
				tax_amount = flt(invoice_tax_map.get(invoice.name, {}).get(tax_acc), tax_amount_precision)
				total_tax += tax_amount


			grouped_invoices[invoice_type]["net_total"] += base_net_total or invoice.base_net_total
			grouped_invoices[invoice_type]["tax_total"] += total_tax
			grouped_invoices[invoice_type]["grand_total"] += invoice.base_grand_total
			grouped_invoices[invoice_type]["outstanding_total"] += invoice.outstanding_amount
			

		data = []
		for invoice_type, totals in grouped_invoices.items():
			row = {
			"ehc_invoice_type": invoice_type,
			"net_total": totals["net_total"],
			"tax_total": totals["tax_total"],
			"grand_total": totals["grand_total"],
			"outstanding_amount": totals["outstanding_total"],
			}
			data.append(row)

		return columns, data
	elif filters.get("summary") == 'Revenue Type':
		invoice_list = get_invoices(filters, additional_query_columns)
		columns, income_accounts, tax_accounts, unrealized_profit_loss_accounts = get_columns(filters,
			invoice_list, additional_table_columns
		)
		if not invoice_list:
			return columns, invoice_list
		grouped_invoices = {}
		company_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")
		invoice_income_map = get_invoice_income_map(invoice_list)
		invoice_income_map, invoice_tax_map = get_invoice_tax_map(
			invoice_list, invoice_income_map, income_accounts
		)
		for invoice in invoice_list:
			revenue_type = invoice.get("ehc1_revenue_type")
			if revenue_type not in grouped_invoices:
				grouped_invoices[revenue_type] = {
				"net_total": 0,
				"tax_total": 0,
				"grand_total": 0,
				"outstanding_total": 0,
			}
			# net total
				
			base_net_total = 0
			for income_acc in income_accounts:
				if invoice.is_internal_customer and invoice.company == invoice.represents_company:
					income_amount = 0
				else:
					income_amount = flt(invoice_income_map.get(invoice.name, {}).get(income_acc))

				base_net_total += income_amount

			# tax amount
			total_tax = 0
			for tax_acc in tax_accounts:
				if tax_acc not in income_accounts:
					tax_amount_precision = (
					get_field_precision(
					frappe.get_meta("Sales Taxes and Charges").get_field("tax_amount"), currency=company_currency
					)
					or 2
				)
				tax_amount = flt(invoice_tax_map.get(invoice.name, {}).get(tax_acc), tax_amount_precision)
				total_tax += tax_amount


			grouped_invoices[revenue_type]["net_total"] += base_net_total or invoice.base_net_total
			grouped_invoices[revenue_type]["tax_total"] += total_tax
			grouped_invoices[revenue_type]["grand_total"] += invoice.base_grand_total
			grouped_invoices[revenue_type]["outstanding_total"] += invoice.outstanding_amount
			

		data = []

		for revenue_type, totals in grouped_invoices.items():
			row = {
			"ehc_invoice_type": revenue_type,
			"net_total": totals["net_total"],
			"tax_total": totals["tax_total"],
			"grand_total": totals["grand_total"],
			"outstanding_amount": totals["outstanding_total"],
			}
			data.append(row)

		return columns, data
	else:
		invoice_list = get_invoices(filters, additional_query_columns)
		columns, income_accounts, tax_accounts, unrealized_profit_loss_accounts = get_columns(filters,
			invoice_list, additional_table_columns
		)
		if not invoice_list:
			return columns, invoice_list
		invoice_income_map = get_invoice_income_map(invoice_list)
		internal_invoice_map = get_internal_invoice_map(invoice_list)
		invoice_income_map, invoice_tax_map = get_invoice_tax_map(
			invoice_list, invoice_income_map, income_accounts
		)
		# Cost Center & Warehouse Map
		invoice_cc_wh_map = get_invoice_cc_wh_map(invoice_list)
		invoice_so_dn_map = get_invoice_so_dn_map(invoice_list)
		company_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")
		mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])

		# data = []
		for inv in invoice_list:
			# invoice details
			accounting_department = list(set(invoice_so_dn_map.get(inv.name, {}).get("accounting_department", [])))
			delivery_note = list(set(invoice_so_dn_map.get(inv.name, {}).get("delivery_note", [])))
			cost_center = list(set(invoice_cc_wh_map.get(inv.name, {}).get("cost_center", [])))
			warehouse = list(set(invoice_cc_wh_map.get(inv.name, {}).get("warehouse", [])))

			row = {
				"invoice": inv.name,
				"posting_date": inv.posting_date,
				"customer": inv.customer,
				"customer_name": inv.customer_name,
			}

			if additional_query_columns:
				for col in additional_query_columns:
					row.update({col: inv.get(col)})
			row.update(
				{
					"customer_group": inv.get("customer_group"),
					"territory": inv.get("territory"),
					"ehc_invoice_type": inv.get("ehc_invoice_type"),
					"receivable_account": inv.debit_to,
					"mode_of_payment": ", ".join(mode_of_payments.get(inv.name, [])),
					"project": inv.project,
					"owner": inv.owner,
					"remarks": inv.remarks,
					"accounting_department": inv.accounting_department,
					"delivery_note": ", ".join(delivery_note),
					"cost_center": ", ".join(cost_center),
					"warehouse": ", ".join(warehouse),
					"currency": company_currency,
				}
			)

			# map income values
			base_net_total = 0
			for income_acc in income_accounts:
				if inv.is_internal_customer and inv.company == inv.represents_company:
					income_amount = 0
				else:
					income_amount = flt(invoice_income_map.get(inv.name, {}).get(income_acc))

				base_net_total += income_amount
				row.update({frappe.scrub(income_acc): income_amount})

			# Add amount in unrealized account
			for account in unrealized_profit_loss_accounts:
				row.update(
					{frappe.scrub(account + "_unrealized"): flt(internal_invoice_map.get((inv.name, account)))}
				)

			# net total
			row.update({"net_total": base_net_total or inv.base_net_total})

			# tax account
			total_tax = 0
			for tax_acc in tax_accounts:
				if tax_acc not in income_accounts:
					tax_amount_precision = (
						get_field_precision(
							frappe.get_meta("Sales Taxes and Charges").get_field("tax_amount"), currency=company_currency
						)
						or 2
					)
					tax_amount = flt(invoice_tax_map.get(inv.name, {}).get(tax_acc), tax_amount_precision)
					total_tax += tax_amount
					row.update({frappe.scrub(tax_acc): tax_amount})

			# total tax, grand total, outstanding amount & rounded total

			row.update(
				{
					"tax_total": total_tax,
					"grand_total": inv.base_grand_total,
					"rounded_total": inv.base_rounded_total,
					"outstanding_amount": inv.outstanding_amount,
				}
			)

			data.append(row)

		return columns, data


def get_columns(filters,invoice_list, additional_table_columns):
	income_accounts = []
	tax_accounts = []
	income_columns = []
	tax_columns = []
	unrealized_profit_loss_accounts = []
	unrealized_profit_loss_account_columns = []
	if filters.get('summary'):
		if invoice_list:
			invoice_items = frappe.get_all(
				"Sales Invoice Item",
				filters={"docstatus": ["!=", 2]},
				fields=["income_account"]
				)
			income_accounts = list({item["income_account"] for item in invoice_items if item["income_account"]})
			taxes_and_charges = frappe.get_all(
				"Sales Taxes and Charges",
				filters={
					"docstatus": ["!=", 2],
					"parenttype": "Sales Invoice",
					"base_tax_amount_after_discount_amount": (">", 0)
				},
				fields=["account_head"]
				)
			tax_accounts = list({tax["account_head"] for tax in taxes_and_charges if tax["account_head"]})
			invoices = frappe.get_all(
				"Sales Invoice",
				filters={
					"docstatus": ["!=", 2],
					"is_internal_customer": 1,
					"unrealized_profit_loss_account": ("!=", "")
				},
				fields=["unrealized_profit_loss_account"]
				)
			unrealized_profit_loss_accounts = list({invoice["unrealized_profit_loss_account"] for invoice in invoices if invoice["unrealized_profit_loss_account"]})
		columns = [
		{"label": _(filters.get('summary')), "fieldname": "ehc_invoice_type", "fieldtype": "Link", "options": "Invoice Type"},
		{"label": _("Sum of Net Total"), "fieldname": "net_total", "fieldtype": "Currency", "options": "currency"},
		{"label": _("Sum of Tax Total"), "fieldname": "tax_total", "fieldtype": "Currency", "options": "currency"},
		{"label": _("Sum of Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "options": "currency"},
		{"label": _("Sum of Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "options": "currency"},
	]
		return columns, income_accounts, tax_accounts, unrealized_profit_loss_accounts
	else:
		"""return columns based on filters"""
		columns = [
			{
				"label": _("Invoice"),
				"fieldname": "invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": 120,
			},
			{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 130},
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 130,
			},
			{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
		]

		if additional_table_columns:
			columns += additional_table_columns

		columns += [
			{
				"label": _("Customer Group"),
				"fieldname": "customer_group",
				"fieldtype": "Link",
				"options": "Customer Group",
				"width": 120,
				"hidden": 1,
			},
			{
				"label": _("Territory"),
				"fieldname": "territory",
				"fieldtype": "Link",
				"options": "Territory",
				"width": 80,
				"hidden": 1,
			},
			{"label": _("Invoice Type"), "fieldname": "ehc_invoice_type", "fieldtype": "Link","options": "Invoice Type", "width": 120},
			{
				"label": _("Receivable Account"),
				"fieldname": "receivable_account",
				"fieldtype": "Link",
				"options": "Account",
				"width": 80,
				"hidden": 1,
			},
			{
				"label": _("Mode Of Payment"),
				"fieldname": "mode_of_payment",
				"fieldtype": "Data",
				"width": 120,
				"hidden": 1,
			},
			{
				"label": _("Project"),
				"fieldname": "project",
				"fieldtype": "Link",
				"options": "Project",
				"width": 80,
				"hidden": 1,
			},
			{"label": _("Owner"), "fieldname": "owner", "fieldtype": "Data", "width": 150, "hidden": 1,},
			{"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 150, "hidden": 1,},
			{
				"label": _("Accounting Department"),
				"fieldname": "accounting_department",
				"fieldtype": "Link",
				"options": "Accounting Department",
				"width": 180,
				"hidden": 0,
			},
			{
				"label": _("Delivery Note"),
				"fieldname": "delivery_note",
				"fieldtype": "Link",
				"options": "Delivery Note",
				"width": 100,
				"hidden": 1,
			},
			{
				"label": _("Cost Center"),
				"fieldname": "cost_center",
				"fieldtype": "Link",
				"options": "Cost Center",
				"width": 100,
			},
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 100,
				"hidden": 1,
			},
			{"fieldname": "currency", "label": _("Currency"), "fieldtype": "Data", "width": 80, "hidden": 1,},
		]
		income_accounts = []
		tax_accounts = []
		income_columns = []
		tax_columns = []
		unrealized_profit_loss_accounts = []
		unrealized_profit_loss_account_columns = []

		if invoice_list:
			invoice_items = frappe.get_all(
				"Sales Invoice Item",
				filters={"docstatus": ["!=", 2]},
				fields=["income_account"]
				)
			income_accounts = list({item["income_account"] for item in invoice_items if item["income_account"]})
			taxes_and_charges = frappe.get_all(
				"Sales Taxes and Charges",
				filters={
					"docstatus": ["!=", 2],
					"parenttype": "Sales Invoice",
					"base_tax_amount_after_discount_amount": (">", 0)
				},
				fields=["account_head"]
				)
			tax_accounts = list({tax["account_head"] for tax in taxes_and_charges if tax["account_head"]})
			invoices = frappe.get_all(
				"Sales Invoice",
				filters={
					"docstatus": ["!=", 2],
					"is_internal_customer": 1,
					"unrealized_profit_loss_account": ("!=", "")
				},
				fields=["unrealized_profit_loss_account"]
				)
			unrealized_profit_loss_accounts = list({invoice["unrealized_profit_loss_account"] for invoice in invoices if invoice["unrealized_profit_loss_account"]})
		for account in income_accounts:
			income_columns.append(
				{
					"label": account,
					"fieldname": frappe.scrub(account),
					"fieldtype": "Currency",
					"options": "currency",
					"width": 120,
					"hidden": 1,
				}
			)

		for account in tax_accounts:
			if account not in income_accounts:
				tax_columns.append(
					{
						"label": account,
						"fieldname": frappe.scrub(account),
						"fieldtype": "Currency",
						"options": "currency",
						"width": 120,
						"hidden": 1,
					}
				)

		for account in unrealized_profit_loss_accounts:
			unrealized_profit_loss_account_columns.append(
				{
					"label": account,
					"fieldname": frappe.scrub(account + "_unrealized"),
					"fieldtype": "Currency",
					"options": "currency",
					"width": 120,
					"hidden": 1,
				}
			)

		net_total_column = [
			{
				"label": _("Net Total"),
				"fieldname": "net_total",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 130,
			}
		]

		total_columns = [
			{
				"label": _("Tax Total"),
				"fieldname": "tax_total",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 130,
			},
			{
				"label": _("Grand Total"),
				"fieldname": "grand_total",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 130,
			},
			{
				"label": _("Rounded Total"),
				"fieldname": "rounded_total",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
				"hidden": 1,
			},
			{
				"label": _("Outstanding Amount"),
				"fieldname": "outstanding_amount",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 180,
			},
		]

		columns = (
			columns
			+ income_columns
			+ unrealized_profit_loss_account_columns
			+ net_total_column
			+ tax_columns
			+ total_columns
		)

		return columns, income_accounts, tax_accounts, unrealized_profit_loss_accounts
def get_invoices(filters, additional_query_columns):
	si = frappe.qb.DocType("Sales Invoice")
	query = (
		frappe.qb.from_(si)
		.select(
			ConstantColumn("Sales Invoice").as_("doctype"),
			si.name,
			si.posting_date,
			si.debit_to,
			si.project,
			si.customer,
			si.customer_name,
			si.owner,
			si.remarks,
			si.territory,
			si.tax_id,
			si.customer_group,
			si.base_net_total,
			si.base_grand_total,
			si.base_rounded_total,
			si.outstanding_amount,
			si.is_internal_customer,
			si.represents_company,
			si.company,
			si.accounting_department,
			si.ehc_invoice_type,
			si.ehc1_revenue_type,

		)
		.where((si.docstatus !=2))
		.orderby(si.posting_date, si.name, order=Order.desc)
		)

	if additional_query_columns:
		for col in additional_query_columns:
			query = query.select(col)

	if filters.get("customer"):
		query = query.where(si.customer == filters.customer)

	query = get_conditions(filters, query, "Sales Invoice")
	invoices = query.run(as_dict=True)

	return invoices


def get_conditions(filters, query, doctype):
	parent_doc = frappe.qb.DocType(doctype)
	if filters.get("owner"):
		query = query.where(parent_doc.owner == filters.owner)
	if filters.get("from_date"):
		query = query.where(parent_doc.posting_date >= filters.from_date)
	if filters.get("to_date"):
		query = query.where(parent_doc.posting_date <= filters.to_date)
	if filters.get("mode_of_payment"):
		payment_doc = frappe.qb.DocType("Sales Invoice Payment")
		query = query.inner_join(payment_doc).on(parent_doc.name == payment_doc.parent)
		query = query.where(payment_doc.mode_of_payment == filters.mode_of_payment).distinct()

	if filters.get("ehc_invoice_type"):
		query = query.where(parent_doc.ehc_invoice_type == filters.ehc_invoice_type)

	if filters.get("revenue_type"):
		query = query.where(parent_doc.ehc1_revenue_type == filters.revenue_type)

	if filters.get("cost_center"):
		costcenter = tuple(filters["cost_center"]) 
		query = query.where(parent_doc.cost_center.isin(costcenter))
	
	accounting_dimensions = get_accounting_dimensions(as_list=False)
	if accounting_dimensions:
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
					filters[dimension.fieldname] = get_dimension_with_children(
						dimension.document_type, filters.get(dimension.fieldname)
					)
				fieldname = dimension.fieldname
				query = query.where(parent_doc[fieldname].isin(filters[fieldname]))
	return query
