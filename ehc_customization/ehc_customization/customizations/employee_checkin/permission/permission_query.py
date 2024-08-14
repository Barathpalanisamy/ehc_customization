import frappe

def reports_to(employee_checkin):
    if frappe.session.user != "Administrator":
        user_details, employee_name = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, ['name','employee_name'])
        owner = frappe.db.get_all('Employee Checkin',{'employee_name':employee_name}, ['name'])
        if user_details:
            get_employee = frappe.db.get_list('Employee',{'reports_to':user_details},pluck='name')
            user_names = set()
            if get_employee:
                for user in get_employee:
                    get_checkin = frappe.db.get_all('Employee Checkin',{'employee':user}, ['name'])
                    if get_checkin:
                        user_names.update([request['name'] for request in get_checkin])      
            if owner:
                user_names.update([request['name'] for request in owner])
            if user_names:     
                user_names_str = "', '".join(user_names)
                return f"""(`tabEmployee Checkin`.name IN ('{user_names_str}'))"""
            return ""
        return ""
    return ""

@frappe.whitelist()
def check_read_only(user):
    get_name = frappe.db.get_value('Employee', {'user_id':user}, 'name')
    if frappe.db.get_all('Employee', {'reports_to':get_name},['name']):
        return 'Manager'
    else:
        return 'Employee'