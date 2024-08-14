# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data



def get_columns():
	columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150,
		},
		{
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Data",
            "width": 120,
        },
		{
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 80,
        },
		{
            "label": _("Total Working Hours"),
            "fieldname": "total_working_hours",
            "fieldtype": "Data",
            "width": 120,
			"precision": 2
        },
		{
            "label": _("Attendance Hours"),
            "fieldname": "attendance_hours",
            "fieldtype": "Data",
            "width": 120,
        },
		{
            "label": _("Permission Hours"),
            "fieldname": "permission_hours",
            "fieldtype": "Data",
            "width": 120,
        },
		{
            "label": _("Reason"),
            "fieldname": "reason",
            "fieldtype": "Data",
            "width": 180,
        },
		{
            "label": _("Allocated Hours"),
            "fieldname": "allocated_time",
            "fieldtype": "Float",
            "width": 150,
			"precision": 2
        },
		{
            "label": _("Available Hours"),
            "fieldname": "available_time",
            "fieldtype": "Float",
            "width": 150,
			"precision": 2
        },
		
	]

	return columns

def get_data(filters):
	employee_name = {'employee': filters.get('employee_name')} if filters.get('employee_name') else {}

	get_atendance = frappe.db.get_all('Attendance', employee_name, ['employee', 'employee_name','name','attendance_date', 'status', 'working_hours'])
	data = []
	for val in get_atendance:
		if ((frappe.db.get_value('Permission Policy Assignment', {'employee':val.employee}, ['time_interval'])).lower() == filters.get('time_interval')) or not filters.get('time_interval'):

			row = {}
			row['employee'] = val.employee
			row['date'] = val.attendance_date
			row['status'] = val.status
			row['total_working_hours'] = val.working_hours
			if filters.get('month'):
				if int(row['date'].month) == int(filters.get('month')):
					data.append(row)
			else:
				data.append(row)
			for type in frappe.db.get_list('Permission Type', pluck='name'):
				get_policy = frappe.db.get_value('Permission Policy Assignment', {'employee':val.employee}, ['name'])	
				get_interval = frappe.db.get_value('Permission Policy Assignment', {'employee':val.employee}, ['time_interval'])	
				if get_policy:
					get_allocated_time = frappe.db.get_value('Time Allocation', {'parent':get_policy, 'permission_type':type, 'month':(val.attendance_date).strftime('%B')}, ['allocated_time'])
					if not get_allocated_time:
						get_allocated_time = 0
				else:
					get_allocated_time = 0
		
				try:
					get_request = frappe.db.get_all('Attendance Request', {'custom_attendance':val.name, 'custom_reason':type}, ['custom_reason', 'start_time', 'end_time', 'name'])	
					hour = 0
					if get_request:
						for d in get_request:
							time_difference = d.get('end_time') - d.get('start_time')
							hours = time_difference.total_seconds() / 3600
							hour += hours
				except:
					hour = 0
				if filters.get('month'):
					if int(row['date'].month) == int(filters.get('month')):
						data.append({'employee':'', 'date':'', 'status':'', 'total_working_hours':'', 'reason':type, 'available_time':abs(get_allocated_time - hour), 'allocated_time': get_allocated_time})
				else:
					data.append({'employee':'', 'date':'', 'status':'', 'total_working_hours':'', 'reason':type, 'available_time':abs(get_allocated_time - hour), 'allocated_time': get_allocated_time})
			
			get_request = frappe.db.get_all('Attendance Request', {'custom_attendance':val.name}, ['custom_reason', 'start_time', 'end_time', 'name'])	
			hour = 0
			if get_request:
				for d in get_request:
					time_difference = d.get('end_time') - d.get('start_time')
					hours = time_difference.total_seconds() / 3600
					hour += hours
			row['permission_hours'] = hour
			row['attendance_hours'] = val.working_hours - hour

	return data