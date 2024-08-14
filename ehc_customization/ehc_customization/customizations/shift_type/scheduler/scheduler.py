from hrms.hr.doctype.shift_type.shift_type import process_auto_attendance_for_all_shifts


def trigger_attendance():
    process_auto_attendance_for_all_shifts()
