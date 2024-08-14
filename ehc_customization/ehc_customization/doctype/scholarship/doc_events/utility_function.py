import frappe
import json
from frappe import _
from frappe.utils import get_datetime
from datetime import datetime

def validate(doc, method=None):
    check_exists = frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1})

    if check_exists and frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1,'scholarship_id':doc.scholarship_id,'processing':'End'}):
        frappe.throw(_('Scholarship Id Already Ended, Select Correct One'))
    if not check_exists and doc.processing != 'Start':
        frappe.throw(_('Scholarship Not Started for this Employee. Please Start First'))
    if check_exists and doc.processing == 'Start' and doc.scholarship_id and not len(frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1,'scholarship_id':doc.scholarship_id,'processing':'End'},['processing']))>0:
        frappe.throw(_('Scholarship Already Started for this Employee. Please Extend or End'))
    if check_exists and len(frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1,'end_date':['between',[(doc.start_date),(doc.end_date)]],'start_date':['between',[(doc.start_date),(doc.end_date)]]})) > 0:
        frappe.throw(_('Scholarship Already Assigned For this Time Period'))
    if check_exists and len(frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1,'scholarship_id':doc.scholarship_id,'processing':'End'})) > 0 and doc.processing=='End':
        frappe.throw(_('Scholarship Already Ended'))
    if check_exists and len(frappe.db.get_all('Scholarship', {'employee':doc.employee,'docstatus':1,'scholarship_id':doc.scholarship_id,'processing':'End'})) > 0 and doc.processing=='Extend':
        frappe.throw(_('Scholarship Already Ended, Create New or Start'))
    if doc.processing=='End' and check_exists:
        # get_doc = frappe.get_doc('Scholarship', doc.scholarship_id)
        # get_doc.is_end = 1
        # get_doc.save()
        frappe.db.set_value('Scholarship',doc.scholarship_id,'is_end',1)

    if doc.scholarship_id:
        update_button = frappe.db.get_all('Scholarship', {'employee':doc.employee, 'docstatus':1, 'scholarship_id':doc.scholarship_id, 'update_button':0},['name'])
        if update_button:
            for val in update_button:
                frappe.db.set_value('Scholarship',val.name,'update_button',1)

        start_button = frappe.db.get_all('Scholarship', {'employee':doc.employee, 'docstatus':1, 'name':doc.scholarship_id, 'update_button':0},['name'])
        if start_button:
            for val in start_button:
                frappe.db.set_value('Scholarship',val.name,'update_button',1)



@frappe.whitelist()
def get_scholarship_id(employee):
    get_employee_id = frappe.db.get_all('Scholarship',{'processing':'Start','is_end':0,'employee':employee},['name'])
    if get_employee_id:
        get_linked = frappe.db.get_all('Scholarship', filters={'scholarship_id': get_employee_id[0]['name']}, fields=['name'], order_by='creation desc')
        if get_linked:
            linked_value = get_linked[1]
        else:
            linked_value = None
        return get_employee_id[0], linked_value

@frappe.whitelist()
def end_scholarship(value, doc):
    load = json.loads(doc)
    value = json.loads(value)
    
    if value['end_date'] > load['start_date']:
        frappe.db.set_value('Scholarship',load['name'],'previous_end_date', load['end_date'])
        frappe.db.set_value('Scholarship',load['name'],'end_date',value['end_date'])
        frappe.db.set_value('Scholarship',load['name'],'processing','End')
        
    else:
        frappe.throw(_("Start Date is greater than Today's Date"))


@frappe.whitelist()
def get_button(name):
    return frappe.db.get_value('Scholarship', name, 'update_button')

