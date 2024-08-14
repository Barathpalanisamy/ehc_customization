import frappe

from ehc_customization.ehc_customization.customizations.user.doc_events.utility_functions import (
	fetch_signup_data
)

def after_save(self, method=None):
    fetch_signup_data(self)