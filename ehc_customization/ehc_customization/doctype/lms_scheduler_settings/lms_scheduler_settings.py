# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from ehc_customization.ehc_customization.doctype.lms_scheduler_settings.doc_events.utility import update_frequency

class LMSSchedulerSettings(Document):
	pass

def validate(doc, method=None):
	update_frequency(doc, method)
    


