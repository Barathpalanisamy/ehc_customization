# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
 
def get_columns():

    columns = [
    {"fieldname": "name", "label": _("Job"), "fieldtype": "Link", "options": "Task", "width": 200},
    {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 200},
    {"fieldname": "subject", "label": _("Subject"), "fieldtype": "Data", "width": 200},
    {"fieldname": "progress", "label": _("Progress"), "fieldtype": "Percent", "width": 150},
    {"fieldname": "is_group", "label": _("Group Task"), "fieldtype": "Check", "width": 150},
    {"fieldname": "parent_task", "label": _("Parent Task"), "fieldtype": "Link", "options": "Task", "width": 150},
    ]
    return columns

def get_data(filters):
    top_task = filters.get('top_task')
    initiative = filters.get('is_initiative')
    filters.pop("top_task", None) 
    if top_task:
        filters['parent_task'] = ('is', 'not set')
    if initiative ==0 :
        filters.pop("is_initiative", None) 
        
    results= frappe.get_all('Task',
        fields=["name", "project", "subject", "progress", "is_initiative","parent_task", "is_group"],
        filters=filters,
        order_by="name DESC"
    )
    return results

      