import frappe
from ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions import transfer_entry

def insert_after(doc, method=None):
    if doc.reference_type in ['Employee', 'Department', 'Designation', 'Branch']:
        transfer_entry(doc, method)

def update(doc, method=None):
    if doc.reference_type in ['Employee', 'Department', 'Designation', 'Branch']:
        transfer_entry(doc, method)

def delete(doc, method=None):
    if doc.reference_type in ['Employee', 'Department', 'Designation', 'Branch']:
        transfer_entry(doc, method)

