from ehc_customization.ehc_customization.customizations.budget.override.budget_override import validate_duplicate, validate_restriction
from erpnext.accounts.doctype.budget.budget import Budget

class BudgetOverride(Budget):
    def validate(self):
        validate_duplicate(self)
        self.validate_accounts()
        self.set_null_value()
        self.validate_applicable_for()
        validate_restriction(self)

    def on_update_after_submit(self):
        validate_restriction(self)