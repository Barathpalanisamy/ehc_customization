import frappe

from ehc_customization.ehc_customization.customizations.employee.doc_events.utility_functions import (
	update_employee_permission,
)
from ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions import transfer_entry


def after_save(self, method=None):
	update_employee_permission(self)

def insert_after(doc, method=None):
    transfer_entry(doc, method)

def update(doc, method=None):
    transfer_entry(doc, method)

def delete(doc, method=None):
    transfer_entry(doc, method)
