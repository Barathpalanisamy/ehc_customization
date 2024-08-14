import frappe
from frappe import _
import json
from datetime import datetime, time, date
import calendar
from frappe.utils import add_days, date_diff, format_date, get_link_to_form, getdate
from ehc_customization.ehc_customization.utility.policy_assignment import calculate_permission_type

def validate_request_overlap(self):
    if not self.name:
        self.name = "New Attendance Request"
    Request = frappe.qb.DocType("Attendance Request")

    overlapping_request = (
        frappe.qb.from_(Request)
        .select(Request.name)
        .where(
            (Request.employee == self.employee)
            & (Request.docstatus < 2)
            & (Request.name != self.name)
            & (self.end_time >= Request.start_time)
            & (self.start_time <= Request.end_time)
            & (Request.from_date == datetime.now().date().strftime('%Y-%m-%d'))
        )
    ).run(as_dict=True)

    if overlapping_request:
        self.throw_overlap_error(overlapping_request[0].name)

def validate_allocated_permission(self):
    fiscal_date = datetime.strptime(str(self.from_date), "%Y-%m-%d").year
    check_policy_assignment = frappe.db.get_value('Permission Policy Assignment', {'employee':self.employee,'fiscal_year':str(fiscal_date)+'-'+str(fiscal_date+1)},['name'])
    if not check_policy_assignment:
        check_policy_assignment = frappe.db.get_value('Permission Policy Assignment', {'employee':self.employee,'fiscal_year':str(fiscal_date)},['name'])

    if check_policy_assignment:
        from_date = datetime.strptime(str(self.from_date), "%Y-%m-%d")
        month = calendar.month_name[(from_date).month]
        start_time = datetime.strptime(str(self.start_time), '%H:%M:%S')
        end_time = datetime.strptime(str(self.end_time), '%H:%M:%S')   
        difference = end_time - start_time
        get_available_time = frappe.db.get_value('Time Allocation', {'parent':check_policy_assignment, 'permission_type':self.custom_reason, 'month':month},['allocated_time'])
        if not get_available_time:
            frappe.throw(_('Policy Assignment Not Assigned For this Reason on Specific Month {}').format(month))        
        # get_time_interval = frappe.db.get_value('Permission Policy Assignment', {'name':self.employee},['time_interval'])
        # if get_time_interval != 'Daily':
        #     get_available_time = get_available_time/ 30
        total = 0
        get_total = frappe.db.get_all('Attendance Request', {'employee':self.employee,'from_date':self.from_date, 'custom_reason':self.custom_reason, 'name': ['!=', self.name]}, ['start_time', 'end_time'])
        for i in get_total:
            differences = i.end_time - i.start_time
            total += differences.total_seconds() / 3600
        if (difference.total_seconds() / 3600) > get_available_time or (total > get_available_time):
                frappe.throw(_('Daily Allocated Time {} hrs Exceeded').format(get_available_time))
    else:
        frappe.throw(_('Kindly Create Permission Policy Assignment and Try Later'))


def validate_timing(self):
    get_shift = frappe.db.get_value('Shift Assignment', {'employee': self.employee}, ['shift_type'])
    if get_shift:
        start_time = datetime.strptime(str(self.start_time), '%H:%M:%S').time()
        end_time = datetime.strptime(str(self.end_time), '%H:%M:%S').time()
        start_date = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()      
        end_date = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
        combine_start = datetime.combine(start_date, start_time)
        combine_end = datetime.combine(end_date, end_time)
        start_datetime = datetime.combine(datetime.strptime(str(self.from_date), '%Y-%m-%d').date(), datetime.min.time())
        end_datetime = datetime.combine(datetime.strptime(str(self.to_date), '%Y-%m-%d').date(), datetime.max.time())      
        datetime_list = frappe.db.get_list('Employee Checkin', {'employee':self.employee, 'time': ('between', [start_datetime, end_datetime])}, pluck='time')
        for dt in datetime_list:
            if abs((dt - combine_start).total_seconds()) < 300 or abs((combine_end - dt).total_seconds()) < 300:
                frappe.throw(_("Employee checkin has less than 5 mins difference from start_time or end_time."))
    else:
        frappe.throw(_('Shift Assignment Not Created for Specific Employee'))

def create_checkin_and_checkout(self):
    get_shift = frappe.db.get_value('Shift Assignment', {'employee': self.employee}, ['shift_type'])
    if get_shift:
        create_employee_checkin(self, get_shift, log_type='OUT', date=self.from_date, time=self.start_time)

        create_employee_checkin(self, get_shift, log_type='IN', date=self.to_date, time=self.end_time)     

def create_employee_checkin(self, get_shift, log_type, date, time):
    create_checkin = frappe.new_doc('Employee Checkin')
    create_checkin.employee = self.employee
    create_checkin.employee_name = self.employee_name
    create_checkin.shift = get_shift
    create_checkin.log_type = log_type
    date_custom = datetime.strptime(str(date), '%Y-%m-%d').date()
    time_custom = datetime.strptime(str(time), '%H:%M:%S').time()
    create_checkin.time = datetime.combine(date_custom, time_custom)
    if log_type == 'IN':
        time_difference_in_hours = calculate_time_difference(self)
        create_checkin.custom_permission_hours = time_difference_in_hours
        create_checkin.custom_attendance_request = self.name

    create_checkin.save()

def calculate_time_difference(self):
    start_time = datetime.strptime(str(self.start_time), '%H:%M:%S')
    end_time = datetime.strptime(str(self.end_time), '%H:%M:%S')   
    time_difference = end_time - start_time
    time_difference_in_hours = time_difference.total_seconds() / 3600
    return time_difference_in_hours

def update_checkin_and_checkout(self):
    get_shift = frappe.db.get_value('Shift Assignment', {'employee': self.employee}, ['shift_type'])
    if get_shift:

        existing_checkin_in = frappe.db.exists({
            'doctype': 'Employee Checkin',
            'employee': self.employee,
            'custom_attendance_request': self.name,
            "log_type": 'IN'
        })
        if existing_checkin_in:
            checkin_in_doc = frappe.get_doc('Employee Checkin', existing_checkin_in)
            checkin_in_doc.employee_name = self.employee_name
            time_difference_in_hours = calculate_time_difference(self)
            checkin_in_doc.custom_permission_hours = time_difference_in_hours
            to_date = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
            end_time = datetime.strptime(str(self.end_time), '%H:%M:%S').time()
            checkin_in_doc.time = datetime.combine(to_date, end_time)
            checkin_in_doc.save()

def create_attendance_records(self):
    request_days = date_diff(self.to_date, self.from_date) + 1
    for day in range(request_days):
        attendance_date = add_days(self.from_date, day)
        if self.should_mark_attendance(attendance_date):
            create_or_update_attendance(self, attendance_date)

def create_or_update_attendance(self, date: str):
    attendance_name = self.get_attendance_record(date)
    status = self.get_attendance_status(date)
    if attendance_name:
        frappe.throw(_('Attendance Already Created'))


@frappe.whitelist()
def update_available_hours(doc):
    load = json.loads(doc)
    check_policy_assignment = frappe.db.get_value('Permission Policy Assignment', {'employee':load['employee']},['name'])
    if check_policy_assignment:
        from_date = datetime.strptime(load['from_date'], "%Y-%m-%d")
        month = calendar.month_name[(from_date).month]   
        get_available_time = frappe.db.get_value('Time Allocation', {'parent':check_policy_assignment, 'permission_type':load['custom_reason'], 'month':month},['allocated_time'])
        if not get_available_time:
            frappe.throw(_('Policy Assignment Not Assigned For this Reason on Specific Month {}').format(month))
        # get_time_interval = frappe.db.get_value('Permission Policy Assignment', {'name':load['employee']},['time_interval'])
        # if get_time_interval != 'Daily':
        #     get_available_time = get_available_time/ 30

        return get_available_time
    return 0

