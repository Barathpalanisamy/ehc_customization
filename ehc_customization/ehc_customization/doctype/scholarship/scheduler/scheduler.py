import frappe
from frappe.utils import get_datetime

def update_end_status():
    get_start_details = frappe.db.get_list('Scholarship', {'processing':'start', 'docstatus':1},pluck='name')
    for entries in get_start_details:
        check_extend = frappe.db.get_all('Scholarship', {'scholarship_id':entries, 'docstatus':1},['*'])
        if not check_extend:
            check_date = frappe.db.get_value('Scholarship', {'name':entries},['end_date'])
            if get_datetime(check_date) < get_datetime(frappe.utils.today()):
                frappe.db.set_value('Scholarship', entries, 'processing', 'End')
                frappe.db.set_value('Scholarship',entries,'is_end',1)
        else:
            sorted_data = sorted(check_extend, key=lambda x: x['modified'], reverse=True)
            processing_end_present = any(item.get('processing') == 'End' for item in sorted_data)
            if not processing_end_present:
                if sorted_data[0]['processing'] == 'Extend':
                    if get_datetime(sorted_data[0]['end_date']) < get_datetime(frappe.utils.today()):
                        frappe.db.set_value('Scholarship', sorted_data[0]['name'], 'processing', 'End')
                        frappe.db.set_value('Scholarship',sorted_data[0]['name'],'is_end',1)
        
