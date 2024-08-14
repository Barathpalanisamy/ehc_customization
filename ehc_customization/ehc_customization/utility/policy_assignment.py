import frappe
from frappe import _
import calendar
from datetime import datetime
import json
from frappe.utils import (
	comma_and,
	get_link_to_form,
)
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def calculate_time(doc):
    load = json.loads(doc)
    get_allocation_time = load['time_allocation']
    time_allocation = []
    for val in get_allocation_time:
        if len(load['fiscal_year']) > 4:
            f_year = int((load['fiscal_year'].split('-'))[0])
        else:
            f_year = int(load['fiscal_year'])
        start_date, end_date = get_date_range(f_year, val['month'])
        get_request = frappe.db.get_all('Attendance Request', {'employee':load['employee'],'from_date':('between', [start_date, end_date])}, ['start_time', 'end_time'])
        if get_request:
            total_time_difference = 0
            for i in get_request:
                time_difference = i.end_time - i.start_time
                time_difference_seconds = time_difference.total_seconds()
                time_difference = time_difference_seconds / 3600.0
                total_time_difference += time_difference
            if val['allocated_time'] >= total_time_difference:
                val['available_time'] = (val['allocated_time'] - total_time_difference)
                time_allocation.append(val)
        else:
            val['available_time'] = (val['allocated_time'])
            time_allocation.append(val)

    return time_allocation

def get_date_range(year, month):
    month = datetime.strptime(month, '%B').month
    num_days = calendar.monthrange(year, month)[1]
    start_date = f'{year}-{month:02d}-01'
    end_date = f'{year}-{month:02d}-{num_days:02d}'

    return start_date, end_date		


@frappe.whitelist()
def create_policy_for_multiple_employees(employees, data):
    if isinstance(employees, str):
        employees = json.loads(employees)

    if isinstance(data, str):
        data = frappe._dict(json.loads(data))

    docs_name = []
    failed = []
  
    for employee in employees:
        existing_assignment = frappe.get_all("Permission Policy Assignment", filters={"employee": employee, 'docstatus':0})
        if existing_assignment:
            # Update existing document
            assignment = frappe.get_doc("Permission Policy Assignment", existing_assignment[0].name)
        else:
            assignment = frappe.new_doc("Permission Policy Assignment")
        assignment.employee = employee
        assignment.title = employee
        assignment.fiscal_year = frappe.db.get_value('Permission Policy', {'name':data['permission_policy']}, ['fiscal_year'])
        assignment.time_interval = frappe.db.get_value('Permission Policy', {'name':data['permission_policy']}, ['time_interval'])
        get_policy_hours = frappe.db.get_all('Permission hours', {'parent':data['permission_policy']}, ['*'])
        time_allocation = []
        allocation_entries = frappe.get_all("Time Allocation", filters={"parent": employee})
        # Iterate over each entry and delete it
        for entry in allocation_entries:
            frappe.delete_doc("Time Allocation", entry.name)
        for val in get_policy_hours:
            create_time_allocation = frappe.new_doc('Time Allocation')
            create_time_allocation.month = val.month
            create_time_allocation.permission_type = val.permission_type
            create_time_allocation.allocated_time = val.allocated_time
            create_time_allocation.parent = employee
            create_time_allocation.parenttype = 'Monthly Allocation'
            create_time_allocation.save()
            time_allocation.append(create_time_allocation)
            if len(assignment.fiscal_year) > 4:
                f_year = int((assignment.fiscal_year.split('-'))[0])
            else:
                f_year = int(assignment.fiscal_year)
            start_date, end_date = get_date_range(f_year, val.month)
        
            get_request = frappe.db.get_all('Attendance Request', {'employee':employee,'reason':val.permission_type,'from_date':('between', [start_date, end_date])}, ['start_time', 'end_time'])
            if get_request:
                total_time_difference = 0
                for i in get_request:
                    time_difference = i.end_time - i.start_time
                    time_difference_seconds = time_difference.total_seconds()
                    time_difference = time_difference_seconds / 3600.0
                    total_time_difference += time_difference
                create_time_allocation.available_time = (val.allocated_time - total_time_difference)
            else:
                create_time_allocation.available_time = val.allocated_time

        # Set child table field of Monthly Time Allocation document
        assignment.set('monthly_allocation', time_allocation)
        assignment.custom_permission_policy = data['permission_policy']

        savepoint = "before_assignment_submission"
        try:
            frappe.db.savepoint(savepoint)
            assignment.flags.ignore_validate = True
            assignment.save()
        except Exception as e:
            frappe.db.rollback(save_point=savepoint)
            assignment.log_error("Permission Policy submission failed")
            failed.append(assignment.name)

        docs_name.append(assignment.name)

    if failed:
        show_assignment_submission_status(failed)

    return docs_name

def validate():
    pass

def show_assignment_submission_status(failed):
	frappe.clear_messages()
	assignment_list = [get_link_to_form("Monthly Time Allocation", entry) for entry in failed]

	msg = _("Failed to submit some Permission policy assignments:")
	msg += " " + comma_and(assignment_list, False) + "<hr>"
	msg += (
		_("Check {0} for more details")
		.format("<a href='/app/List/Error Log?reference_doctype=Monthly Time Allocation'>{0}</a>")
		.format(_("Error Log"))
	)

	frappe.msgprint(
		msg,
		indicator="red",
		title=_("Submission Failed"),
		is_minimizable=True,
	)


@frappe.whitelist()
def calculate_monthly_time(doc):
    load = json.loads(doc)
    get_allocation_time = frappe.db.get_all('Permission hours',{'parent':load['custom_permission_policy']}, ['*'])
    permission = []
    for i in get_allocation_time:
        create_doc = frappe.new_doc('Time Allocation')
        create_doc.month = i['month']
        create_doc.permission_type = i['permission_type']
        create_doc.allocated_time = i['allocated_time']
        # create_doc.parent = 'Permission Policy Assignment'
        # create_doc.parenttype = 'Monthly Allocation'
        fiscal = frappe.db.get_value('Permission Policy',{'name':load['custom_permission_policy']}, ['fiscal_year'])
        if len(fiscal) > 4:
            f_year = int((fiscal.split('-'))[0])
        else:
            f_year = int(fiscal)
        start_date, end_date = get_date_range(f_year, i['month'])
        try:
            get_request = frappe.db.get_all('Attendance Request', {'employee':load['employee'],'custom_reason':i['permission_type'], 'from_date':('between', [start_date, end_date])}, ['start_time', 'end_time'])
        except:
            get_request = []
        if get_request:
            total_time_difference = 0
            for ii in get_request:
                time_difference = ii.end_time - ii.start_time
                time_difference_seconds = time_difference.total_seconds()
                time_difference = time_difference_seconds / 3600.0
                total_time_difference += time_difference
            
            create_doc.available_time = i['available_time'] - total_time_difference
        else:
            create_doc.available_time = i['available_time']
        # create_doc.insert()
        permission.append(create_doc.as_dict())
    return permission



month_order = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

@frappe.whitelist()
def calculate_permission_type(doc):
    load = json.loads(doc)
    try:
        get_permission_policy = frappe.db.get_all('Permission Policy Assignment', {'custom_permission_policy':load['employee']}, ['*'])
        for val in get_permission_policy:
            get_assignment = frappe.get_doc('Permission Policy Assignment', val.name)
            permission = []
            allocation_entries = frappe.get_all("Time Allocation", filters={"parent": val.name})
            # Iterate over each entry and delete it
            for entry in allocation_entries:
                frappe.delete_doc("Time Allocation", entry.name)
            for i in load['allocation']:
                create_doc = frappe.new_doc('Time Allocation')
                create_doc.month = i['month']
                create_doc.permission_type = i['permission_type']
                create_doc.allocated_time = i['allocated_time']
                create_doc.parent = 'Permission Policy Assignment'
                create_doc.parenttype = 'Monthly Allocation'
                if len(load['fiscal_year']) > 4:
                    f_year = int((load['fiscal_year'].split('-'))[0])
                else:
                    f_year = int(load['fiscal_year'])

                start_date, end_date = get_date_range(f_year, i['month'])
                get_request = frappe.db.get_all('Attendance Request', {'employee':val['employee'],'custom_reason':i['permission_type'], 'from_date':('between', [start_date, end_date])}, ['start_time', 'end_time'])
                if get_request:
                    total_time_difference = 0
                    for ii in get_request:
                        time_difference = ii.end_time - ii.start_time
                        time_difference_seconds = time_difference.total_seconds()
                        time_difference = time_difference_seconds / 3600.0
                        total_time_difference += time_difference
                    
                 
                    create_doc.available_time = i['available_time'] - total_time_difference
                else:
                    create_doc.available_time = i['available_time']
                create_doc.insert()
                permission.append(create_doc)
            get_assignment.set('monthly_allocation', permission)
            get_assignment.time_interval = load['time_interval']
            get_assignment.save()

    except Exception as err:
        return []

@frappe.whitelist()
def get_policy_type():
    return frappe.db.get_list('Permission Type', pluck='name')

@frappe.whitelist()
def set_entries(value):
    load = json.loads(value)
    list_of_entries = []
    if load['time_interval'] == 'Annual' and len(load) < 4:
        months = [
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December"
            ]
    else:
        months = [load['month']]

    for i in load['selected_items'].strip().split(','):
        if i:
            for month in months:
                dicts = {}
                dicts['month'] = month
                dicts['permission_type'] = i.strip()
                dicts['allocated_time'] = load['allocated_time']
                dicts['available_time'] = load['allocated_time']
                list_of_entries.append(dicts)
    return list_of_entries

@frappe.whitelist()
def make_policy_assignment(source_name, target_doc=None):
    doc = get_mapped_doc(
        "Permission Policy",
        source_name,
        {
            "Permission Policy": {"doctype": "Permission Policy Assignment"},
            "Permission hours": {
                "doctype": "Time Allocation",
            },
        },
        target_doc,
    )

    return doc

@frappe.whitelist()
def make_attendance_request(source_name, target_doc=None):
    doc = get_mapped_doc(
        "Permission Policy Assignment",
        source_name,
        {
            "Permission Policy Assignment": {"doctype": "Attendance Request"},
            # "field_map": {
			# 		"employee": "custom_policy",
            # }
        },
        target_doc,
    )

    return doc
