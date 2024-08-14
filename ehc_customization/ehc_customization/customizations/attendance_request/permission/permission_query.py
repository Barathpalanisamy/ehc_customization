import frappe

def reports_to(attendance_request):
    if frappe.session.user != "Administrator":
        user_details = frappe.db.get_all('Attendance Request', {'custom_reporting_manager': frappe.session.user}, ['name'])
        owner = frappe.db.get_value('Employee', {'user_id':frappe.session.user},['name'])
        if owner:
            owner_value = frappe.db.get_all('Attendance Request', {'employee': owner}, ['name'])
        else:
            owner_value = None
        user_names = set()
        if user_details:
            user_names.update([request['name'] for request in user_details])      
        if owner_value:
            user_names.update([request['name'] for request in owner_value])
        if user_names:
            user_names_str = "', '".join(user_names)
            return f"""(`tabAttendance Request`.name IN ('{user_names_str}'))"""
    return ""

@frappe.whitelist()
def manager_self(employee):
    reports_to = frappe.db.get_value('Employee', employee, 'reports_to')
    if reports_to:
        user_id = frappe.db.get_value('Employee', reports_to, 'user_id')
        return user_id
    return None