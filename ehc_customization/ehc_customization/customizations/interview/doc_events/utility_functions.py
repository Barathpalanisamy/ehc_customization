import frappe

def on_update(doc, events):
    add_user_permission(doc.owner, "Interview", doc.name)
    for interviewer in doc.interview_details:
        add_user_permission(interviewer.interviewer, "Interview", doc.name)
def add_user_permission(user, doctype, docname):
        if not frappe.db.exists("User Permission", {
            "user": user,
            "allow": doctype,
            "for_value": docname
        }):
            user_permission = frappe.new_doc("User Permission")
            user_permission.update({
                "user": user,
                "allow": doctype,
                "for_value": docname,
                "apply_to_all_doctypes": 0
            })
            user_permission.insert(ignore_permissions=True)