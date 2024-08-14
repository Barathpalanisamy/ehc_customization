import frappe
from ehc_customization.ehc_customization.customizations.attendance_request.override.override import(
validate_request_overlap, validate_timing, create_checkin_and_checkout, update_checkin_and_checkout,\
create_attendance_records, validate_allocated_permission
)
from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest
from hrms.hr.utils import validate_active_employee, validate_dates

class AttendanceRequestCreation(AttendanceRequest):
    def validate(self):
        validate_active_employee(self.employee)
        validate_dates(self, self.from_date, self.to_date)
        self.validate_half_day()
        validate_request_overlap(self)
        validate_allocated_permission(self)
        validate_timing(self)

    def on_submit(self):
        create_attendance_records(self)
        create_checkin_and_checkout(self)
                
    def on_update_after_submit(self):
        validate_allocated_permission(self)
        update_checkin_and_checkout(self)
