import frappe
from frappe import _
from frappe.utils import add_months, flt, fmt_money, get_last_day, getdate
from erpnext.controllers.subcontracting_controller import get_item_details
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.budget.budget import get_accumulated_monthly_budget,get_actual_expense,get_requested_amount,get_ordered_amount

class BudgetError(frappe.ValidationError):
	pass

def validate_expense_against_budget(args, doctype, expense_amount=0):
    args = frappe._dict(args)
    if not frappe.get_all("Budget", limit=1):
        return
    if args.get("company") and not args.fiscal_year:
        args.fiscal_year = get_fiscal_year(args.get("posting_date"), company=args.get("company"))[0]
        frappe.flags.exception_approver_role = frappe.get_cached_value(
            "Company", args.get("company"), "exception_budget_approver_role")
    budget_filter = {"fiscal_year": args.fiscal_year, "company": args.company}
    if not frappe.get_cached_value("Budget", budget_filter):
        return
    if not args.account:
        args.account = args.get("expense_account")
    if not (args.get("account") and args.get("cost_center")) and args.item_code:
        args.cost_center, args.account = get_item_details(args)
    if not args.account:
        return
    default_dimensions = [
        {"fieldname": "project", "document_type": "Project"},{"fieldname": "cost_center", "document_type": "Cost Center"},]
    dimension_calculation(default_dimensions, args, expense_amount)

def dimension_calculation(default_dimensions, args, expense_amount):
    for dimension in default_dimensions + get_accounting_dimensions(as_list=False):
        budget_against = dimension.get("fieldname")
        if (args.get(budget_against)and args.account and (frappe.get_cached_value("Account", args.account, "root_type") == "Expense")):
            doctype = dimension.get("document_type")
            if frappe.get_cached_value("DocType", doctype, "is_tree"):
                lft, rgt = frappe.get_cached_value(doctype, args.get(budget_against), ["lft", "rgt"])
                condition = f"and exists(select name from `tab{doctype}` where lft<={lft} and rgt>={rgt} and name=b.{budget_against})"
                args.is_tree = True
            else:
                condition = f"and b.{budget_against}={frappe.db.escape(args.get(budget_against))}"
                args.is_tree = False

            args.budget_against_field = budget_against
            args.budget_against_doctype = doctype
            budget_records = frappe.get_all("Budget",filters={"fiscal_year": args.fiscal_year,"accounting_department": args.accounting_department,
                    "cost_center": args.cost_center,"docstatus": 1,},
                fields=[
                    "name",f"{budget_against} as budget_against","monthly_distribution","applicable_on_material_request",
                    "applicable_on_purchase_order","applicable_on_booking_actual_expenses","action_if_annual_budget_exceeded",
                    "action_if_accumulated_monthly_budget_exceeded","action_if_annual_budget_exceeded_on_mr","action_if_accumulated_monthly_budget_exceeded_on_mr",
                    "action_if_annual_budget_exceeded_on_po","action_if_accumulated_monthly_budget_exceeded_on_po","custom_action_if_accumulated_annual_budget_exceeded",
                    "custom_action_if_accumulated_monthly_budget_exceeded","custom_apply_budget_restrictions"
                ],as_list=False,)
            budget_account_records = frappe.get_all("Budget Account",filters={"parent": ["in", [budget_record.name for budget_record in budget_records]], "account": args.account},
                fields=["parent", "budget_amount"],as_list=False,)

            for budget_record in budget_records:
                budget_record["budget_amount"] = next((ba.budget_amount for ba in budget_account_records if ba.parent == budget_record.name), 0)
            if budget_records:
                if args['docstatus'] < 1:
                    validate_budget_records(args, budget_records, doctype, expense_amount)

def validate_budget_records(args, budget_records, doctype, expense_amount):
    for budget in budget_records:
        if flt(budget.budget_amount):
            if budget.custom_apply_budget_restrictions:
                yearly_action, monthly_action = budget.custom_action_if_accumulated_annual_budget_exceeded, budget.custom_action_if_accumulated_monthly_budget_exceeded
                args["for_material_request"] = 1
                args["for_purchase_order"] = 1
            else:
                yearly_action, monthly_action = 'Ignore', 'Ignore'
            if yearly_action in ("Stop", "Warn"):
                compare_expense_with_budget(
                    args,flt(budget.budget_amount),_("Annual"),yearly_action,budget.budget_against,doctype,
                    expense_amount,
                )
            if monthly_action in ["Stop", "Warn"]:
                budget_amount = get_accumulated_monthly_budget(
                    budget.monthly_distribution, args.posting_date, args.fiscal_year, budget.budget_amount
                )

                args["month_end_date"] = get_last_day(args.posting_date)

                compare_expense_with_budget(
                    args,budget_amount,_("Accumulated Monthly"),monthly_action,budget.budget_against,doctype,
                    expense_amount,
                )

def compare_expense_with_budget(args, budget_amount, action_for, action, budget_against, doctype, amount=0):
    args.actual_expense, args.requested_amount, args.ordered_amount = get_actual_expense(args), 0, 0
    fiscal_year = args['fiscal_year']
    try:
        start_year, end_year = [int(year) for year in fiscal_year.split('-')]
    except:
        start_year, end_year = int(fiscal_year), int(fiscal_year)
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"
    get_list = frappe.db.get_all('Entry Log', {'company':args['company'], 'posting_date':['BETWEEN',[start_date, end_date]], 'cost_center':args['cost_center'], \
                                    'accounting_department': args['accounting_department'], 'expense_account': args['account'], 'doctype_name':['!=',args['parent']], 'workflow_state':0}, ['amount'])
    if get_list:
        total_amount = sum(([int(record['amount']) for record in get_list]) )
    else:
        total_amount = 0
    if args['doctype'] in ['Material Request', 'Purchase Order']:
        args.requested_amount, args.ordered_amount = get_requested_amount(args), get_ordered_amount(args)

        if args.get("doctype") == "Material Request" and args.for_material_request:
           amount = args.requested_amount + args.ordered_amount

        elif args.get("doctype") == "Purchase Order" and args.for_purchase_order:
            amount = args.ordered_amount
        args.actual_expense = amount + total_amount
    else:
        args.actual_expense = args.actual_expense + total_amount
    raise_warnings(args, budget_amount, budget_against, action_for, amount, action)

def raise_warnings(args, budget_amount, budget_against, action_for, amount, action):
    check_value  = frappe.db.get_value('Entry Log',{'child_id':args['name'],'doctype_name':['!=',args['parent']],'workflow_state':0}, ['amount'])
    if check_value and check_value != args['amount']:
        amount = abs(float(check_value) - float(args['amount']))
    total_expense = args.actual_expense + amount

    if total_expense > round(budget_amount):
        error_tense = _("will be")
        diff = total_expense - budget_amount
        currency = frappe.get_cached_value("Company", args.company, "default_currency")
        msg = _("{0} Budget for Account {1} against {2} {3} is {4}. It {5} exceed by {6}").format(
            _(action_for),frappe.bold(args.account),frappe.unscrub(args.budget_against_field),frappe.bold(budget_against),frappe.bold(fmt_money(budget_amount, currency=currency)),
            error_tense,frappe.bold(fmt_money(diff, currency=currency)),)
        if frappe.flags.exception_approver_role and frappe.flags.exception_approver_role in frappe.get_roles(frappe.session.user):
            action = "Warn"
        if action == "Stop":
            frappe.throw(msg, BudgetError, title=_("Budget Exceeded"))
        else:
            frappe.msgprint(msg, indicator="orange", title=_("Budget Exceeded"))