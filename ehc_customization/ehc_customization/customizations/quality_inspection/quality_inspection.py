import frappe
from ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions import do_assignment
def on_update(self,event):
    do_assignment(self)