import frappe
from ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions import transfer_entry

@frappe.whitelist()
def designation_details(responsibility):
	emp_des_doc=frappe.get_doc("Employee Responsibility",responsibility)
	final_list=[]
	for i in emp_des_doc.responsibility:
		final_list.append(i)
	return final_list

def insert_after(self, method=None):
    transfer_entry(self, method)

def update(doc, method=None):
    transfer_entry(doc, method)

def delete(doc, method=None):
    transfer_entry(doc, method)
