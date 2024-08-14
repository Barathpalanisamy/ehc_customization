from ehc_customization.ehc_customization.customizations.data_import.data_import_validate import data_import_validate
import frappe
from frappe.core.doctype.data_import.data_import import DataImport
from ehc_customization.ehc_customization.customizations.data_import.override.data_import_override import validate_file
class DataImportMerge(DataImport):
    def validate(self):
        validate_file(self)
        data_import_validate(self)
        self.validate_import_file()
        self.validate_google_sheets_url()
        self.set_payload_count()