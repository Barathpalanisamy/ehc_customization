# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ehc_customization.ehc_customization.doctype.user_account_profile.doc_events.create_role import (
	create_roles,
)


class UserAccountProfile(Document):
	def validate(self, method=None):
		create_roles(self)
