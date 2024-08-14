import frappe

from ehc_customization.ehc_customization.customizations.job_opening.doc_events.utility_functions import (
	send_notification_for_new_job_opening,validation_on_internal_route 
)

def after_save(self, method=None):
    send_notification_for_new_job_opening(self)
    
def validate(self, method=None):
    validation_on_internal_route(self)