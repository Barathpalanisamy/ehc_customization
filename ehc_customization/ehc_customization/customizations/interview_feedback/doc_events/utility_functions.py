import frappe

def on_submit(doc,events):
    user_permission = frappe.new_doc("User Permission")
    user_permission.update({
        "user": doc.interviewer,
        "allow": "Interview Feedback",
        "for_value": doc.name,
        "apply_to_all_doctypes": 0
    })
    user_permission.insert(ignore_permissions=True)