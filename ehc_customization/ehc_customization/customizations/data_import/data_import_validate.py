import frappe


def data_import_validate(self):
    doc_before_save = self.get_doc_before_save()
    if (
        not (self.import_file or self.google_sheets_url)
        or (doc_before_save and doc_before_save.import_file != self.import_file)
        or (doc_before_save and doc_before_save.google_sheets_url != self.google_sheets_url)
    ):
        self.template_options = ""
        self.template_warnings = ""
