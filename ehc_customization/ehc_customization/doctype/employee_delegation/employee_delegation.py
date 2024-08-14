# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

from ehc_customization.ehc_customization.doctype.employee_delegation.doc_events.utility_functions import (update_employee_references,update_new_employee_details)
from frappe.model.document import Document

class EmployeeDelegation(Document):
    def on_submit(self):
        update_new_employee_details(self)
        update_employee_references(self)





