import json
import os
import frappe
from ehc_customization.ehc_customization.doctype.lms_scheduler_settings.doc_events.utility import update_frequency

def after_migrate():
	create_custom_fields()
	create_property_setter()
	stopped_hourly_scheduler()
	migrate_frequency()


def create_custom_fields():
	CUSTOM_FIELDS = {}
	path = os.path.join(os.path.dirname(__file__), "ehc_customization/custom_fields")
	for file in os.listdir(path):
		with open(os.path.join(path, file), "r") as f:
			CUSTOM_FIELDS.update(json.load(f))
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(CUSTOM_FIELDS)

def create_property_setter():
	print("Creating/Updating Property Setters....")
	path = os.path.join(os.path.dirname(__file__), "ehc_customization/property_setters")
	for file in os.listdir(path):
		with open(os.path.join(path, file), "r") as f:
			property_setters = json.load(f)
			for doctype, properties in property_setters.items():
				for args in properties:
					if not args.get("doctype"):
						args["doctype"] = doctype
					from frappe.custom.doctype.property_setter.property_setter import make_property_setter
					make_property_setter(**args)

def stopped_hourly_scheduler():
	get_job_type = frappe.get_doc('Scheduled Job Type', 'shift_type.process_auto_attendance_for_all_shifts')
	get_job_type.stopped = 1
	get_job_type.save()

def migrate_frequency():
	try:
		doc = frappe.get_doc('LMS Scheduler Settings')
		update_frequency(doc, method = None)
	except:
		pass