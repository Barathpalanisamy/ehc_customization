from erpnext.accounts.doctype.budget.budget import DuplicateBudgetError
import frappe
from frappe import _

def validate_duplicate(self):
    budget_against_field = frappe.scrub(self.budget_against)
    budget_against = self.get(budget_against_field)

    accounts = [d.account for d in self.accounts] or []
    existing_budget = frappe.get_all(
        "Budget",
        filters={
            "docstatus": ("<", 2),
            "company": self.company,
            "accounting_department": self.accounting_department,
            budget_against_field: budget_against,
            "fiscal_year": self.fiscal_year,
            "name": ("!=", self.name)
        },
        fields=["name"]
    )
    existing_budget_accounts = frappe.get_all(
        "Budget Account",
        filters={"parent": ("in", [budget["name"] for budget in existing_budget]), "account": ("in", accounts)},
        fields=["account",'parent']
    )
    if existing_budget_accounts:
        for budget_account in existing_budget_accounts:
            frappe.throw(
                _(
                    "Another Budget record '<b>{0}</b>' already exists against {1} <b>({2})</b> and Accounting Department <b>({5})</b>  and account <b>'{3}'</b> for fiscal year <b>{4}</b>"
                ).format(budget_account['parent'], self.budget_against, budget_against, budget_account["account"], self.fiscal_year,self.accounting_department),
                DuplicateBudgetError,
            )


    # if self.budget_against == "Cost Center" and self.accounting_department:

    #     existing_budget = frappe.get_all(
    #         "Budget",
    #         filters={
    #             "docstatus": ("<", 2),
    #             "company": self.company,
    #             budget_against_field: budget_against,
    #             "fiscal_year": self.fiscal_year,
    #             "accounting_department":("is", "not set"),
    #             "name": ("!=", self.name)

    #         },
    #         fields=["name", "custom_akd_total_base_budget"]
    #     )
    #     total_budget_amount = sum(budget['custom_akd_total_base_budget'] for budget in existing_budget)

    #     existing_budget_cc = frappe.get_all(
    #         "Budget",
    #         filters={
    #             "docstatus": ("<", 2),
    #             "company": self.company,
    #             budget_against_field: budget_against,
    #             "fiscal_year": self.fiscal_year,
    #             "accounting_department": ("is", "set"),
    #             "name": ("!=", self.name)

    #         },
    #         fields=["name", "custom_akd_total_base_budget"]
    #     )

    #     total_budget_amount_cc = sum(budget_cc['custom_akd_total_base_budget'] for budget_cc in existing_budget_cc)
    #     total_budget_amount_cc+=self.custom_akd_total_base_budget
    #     if total_budget_amount:
    #         if total_budget_amount_cc > total_budget_amount:
    #             frappe.throw(_("The combined budget for Cost Center and Accounting Department ({0}) exceeds the limit amount of {1}").format(total_budget_amount_cc,total_budget_amount), DuplicateBudgetError)



    # elif self.budget_against == "Cost Center" and not self.accounting_department:
    #     existing_budget_cc_on = frappe.get_all(
    #         "Budget",
    #         filters={
    #             "docstatus": ("<", 2),
    #             "company": self.company,
    #             budget_against_field: budget_against,
    #             "fiscal_year": self.fiscal_year,
    #             "accounting_department": ("is", "set"),
    #             "name": ("!=", self.name)

    #         },
    #         fields=["name", "custom_akd_total_base_budget"]
    #     )

    #     total_budget_amount_cc_on = sum(budget_cc_on['custom_akd_total_base_budget'] for budget_cc_on in existing_budget_cc_on)
    #     if total_budget_amount_cc_on:
    #         if total_budget_amount_cc_on > self.custom_akd_total_base_budget:
    #             frappe.throw(_("The Cost Center only budget value ({0}) should be grater the combined budget of Cost Center and Accounting Department ({1}) value.").format(self.custom_akd_total_base_budget,total_budget_amount_cc_on), DuplicateBudgetError)



def validate_restriction(self):
    if self.custom_apply_budget_restrictions:
        frappe.db.set_value('Budget',self.name, 'action_if_annual_budget_exceeded', 'Ignore')
        frappe.db.set_value('Budget',self.name, 'action_if_accumulated_monthly_budget_exceeded', 'Ignore')
        frappe.db.set_value('Budget',self.name, 'applicable_on_material_request', 0)
        frappe.db.set_value('Budget',self.name, 'applicable_on_purchase_order', 0)