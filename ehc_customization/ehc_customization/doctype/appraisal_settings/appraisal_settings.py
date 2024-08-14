# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ehc_customization.ehc_customization.doctype.appraisal_settings.doc_events.percentage_validation import percentage_validation

class AppraisalSettings(Document):
	def validate(self):
		percentage_validation(self)
		
