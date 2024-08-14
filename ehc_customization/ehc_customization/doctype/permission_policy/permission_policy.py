# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PermissionPolicy(Document):
	@frappe.whitelist()
	def get_months(self):
		month_list = [
			"January",
			"February",
			"March",
			"April",
			"May",
			"June",
			"July",
			"August",
			"September",
			"October",
			"November",
			"December",
		]
		idx = 1
		for m in month_list:
			mnth = self.append("time_allocation")
			mnth.month = m


