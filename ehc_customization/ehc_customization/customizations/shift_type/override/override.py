import frappe
import itertools
from frappe.utils import cint, create_batch, get_datetime, get_time, getdate
from hrms.hr.doctype.employee_checkin.employee_checkin import (
	calculate_working_hours,
	mark_attendance_and_link_log,
)

EMPLOYEE_CHUNK_SIZE = 50

def trigger_checkin(self):
    if (
        not cint(self.enable_auto_attendance)
        or not self.process_attendance_after
        or not self.last_sync_of_checkin
    ):
        return

    logs = get_employee_checkins(self)
    total = sum(val.custom_permission_hours for val in logs)
    for key, group in itertools.groupby(logs, key=lambda x: (x["employee"], x["shift_start"])):
        single_shift_logs = list(group)
        attendance_date = key[1].date()
        employee = key[0]

        if not self.should_mark_attendance(employee, attendance_date):
            continue

        (
            attendance_status,
            working_hours,
            late_entry,
            early_exit,
            in_time,
            out_time,
        ) = self.get_attendance(single_shift_logs)
        working_hours = working_hours + total
        mark_attendance_and_link_log(
            single_shift_logs,
            attendance_status,
            attendance_date,
            working_hours,
            late_entry,
            early_exit,
            in_time,
            out_time,
            self.name,
        )

    # commit after processing checkin logs to avoid losing progress
    frappe.db.commit()  # nosemgrep

    assigned_employees = self.get_assigned_employees(self.process_attendance_after, True)
    for val in logs:
        if val.custom_attendance_request:
            get_attendance = frappe.db.get_value('Attendance', {'employee':val.employee, 'attendance_date':(val.time).date()})
            if get_attendance:
                frappe.db.set_value('Attendance Request', val.custom_attendance_request, 'custom_attendance', get_attendance)
    # mark absent in batches & commit to avoid losing progress since this tries to process remaining attendance
    # right from "Process Attendance After" to "Last Sync of Checkin"
    for batch in create_batch(assigned_employees, EMPLOYEE_CHUNK_SIZE):
        for employee in batch:
            self.mark_absent_for_dates_with_no_attendance(employee)

        frappe.db.commit()  # nosemgrep
            
def get_employee_checkins(self) -> list[dict]:
    return frappe.get_all(
        "Employee Checkin",
        fields=[
            "name",
            "employee",
            "log_type",
            "time",
            "shift",
            "shift_start",
            "shift_end",
            "shift_actual_start",
            "shift_actual_end",
            "device_id",
            "custom_permission_hours",
            "custom_attendance_request"
        ],
        filters={
            "skip_auto_attendance": 0,
            "attendance": ("is", "not set"),
            "time": (">=", self.process_attendance_after),
            "shift_actual_end": ("<", self.last_sync_of_checkin),
            "shift": self.name,
        },
        order_by="employee,time",
    )