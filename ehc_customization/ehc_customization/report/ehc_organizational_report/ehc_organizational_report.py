# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Count

def execute(filters):
    filters_val={}
    if filters.get("company"):
        filters_val["company"] =  filters.get("company")
    if filters.get("designation"):
        filters_val["designation"] = filters.get("designation")
    if filters.get("employee"):
         filters_val["employee"] =filters.get("employee")
    if filters.get("branch"):
         filters_val["branch"] =filters.get("branch")

    filters_val["status"]="Active"
    columns = get_columns()
    data = get_data(filters_val)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 500
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Designation"),
            "fieldname": "designation",
            "fieldtype": "Link",
            "options": "Designation",
            "width": 150
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 150
        },
        {
            "label": _("Network"),
            "fieldname": "branch",
            "fieldtype": "Link",
            "options": "Branch",
            "width": 150
        },
    ]

def get_data(filters_val):
    data = []
    processed_employees = set() 
    employees = frappe.get_all(
        "Employee",
        fields=["name as employee", "employee_name", "designation", "reports_to","department","branch"],
        filters=filters_val,
        order_by="reports_to"
    )
    for employee in employees:
        if employee.employee in processed_employees:
            continue
        employee.indent = 0
        data.append(employee)
        processed_employees.add(employee.employee)  
        subordinate_data = get_subordinates(employee.employee, employee.indent + 1, processed_employees)
        data.extend(subordinate_data)
    return data

def get_subordinates(manager, indent, processed_employees):
    subordinates = []
    employees = frappe.get_all(
        "Employee",
        fields=["name as employee", "employee_name", "designation","department","branch"],
        filters={"reports_to": manager, "status": "Active"},
        order_by="name"
    )
    for subordinate in employees:
        if subordinate.employee in processed_employees:
            continue
        subordinate.indent = indent
        subordinates.append(subordinate)
        processed_employees.add(subordinate.employee)  
        subordinates.extend(get_subordinates(subordinate.employee, indent + 1, processed_employees))
    return subordinates
