import frappe
from ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions import transfer_entry

def insert_after(self, method=None):
    transfer_entry(self, method)

def update(doc, method=None):
    transfer_entry(doc, method)

def delete(doc, method=None):
    transfer_entry(doc, method)
