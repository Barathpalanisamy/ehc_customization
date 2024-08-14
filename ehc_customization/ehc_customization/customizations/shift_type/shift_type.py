import frappe
from ehc_customization.ehc_customization.customizations.shift_type.override.override import trigger_checkin
from hrms.hr.doctype.shift_type.shift_type import ShiftType

class OverrideShiftType(ShiftType):
    @frappe.whitelist()
    def process_auto_attendance(self):
        trigger_checkin(self)
