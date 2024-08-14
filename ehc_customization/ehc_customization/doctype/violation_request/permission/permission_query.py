import frappe

def reports_to(violation_request):
    if frappe.session.user != "Administrator":
        user_details = frappe.db.get_all('Violation Request', {'user': frappe.session.user}, ['name'])
        owner_details = frappe.db.get_all('Violation Request', {'email_id': frappe.session.user}, ['name'])
        user_names = set()
        if user_details:
            user_names.update([request['name'] for request in user_details])      
        if owner_details:
            user_names.update([request['name'] for request in owner_details])
        if user_names:
            user_names_str = "', '".join(user_names)
            return f"""(`tabViolation Request`.name IN ('{user_names_str}'))"""
    return ""