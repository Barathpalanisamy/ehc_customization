from ehc_customization.ehc_customization.utility.budget_warnings import budget_warnings, create_or_update_entry_log, allow_validation

def validate(self, method=None):
	budget_warnings(self)
	allow_validation(self)

def on_submit(self, method=None):
	if self.docstatus == 1:
		create_or_update_entry_log(self, method)

def after_save(self, method=None):
	create_or_update_entry_log(self, method)

def on_update(self, method=None):
	create_or_update_entry_log(self, method)

def on_cancel(self, method=None):
	create_or_update_entry_log(self, method)
