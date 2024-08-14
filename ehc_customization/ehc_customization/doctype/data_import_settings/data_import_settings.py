# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

from ehc_customization.ehc_customization.doctype.data_import_settings.doc_events.utility_functions import import_columns
from frappe.model.document import Document

class DataImportSettings(Document):
    def validate(self):
        import_columns(self)