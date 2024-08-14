import frappe

from ehc_customization.ehc_customization.customizations.job_applicant.doc_events.utility_functions import (
    send_notification_for_new_job_appicant,
)

def after_save(self, method=None):
    send_notification_for_new_job_appicant(self)