import frappe
from frappe import _
import json
  
# def add_roles_to_user(user,profile):
#     user_doc = frappe.get_doc("User",user)
#     user_doc.role_profile_name = profile
#     user_doc.save(ignore_permissions=True)
    
@frappe.whitelist()     
def get_nat_id(nat_id):
    if not frappe.db.exists("Employee",{"nat_id": nat_id},) and not frappe.db.exists("Job Seeking Users",{"custom_nat_id": nat_id}):
        return 1
    else:
        return 0

def update_password(self):
    if frappe.db.exists("Employee",{"nat_id": self.custom_nat_id},) and frappe.db.exists("Job Seeking Users",{"custom_nat_id": self.custom_nat_id}):
        frappe.throw(_('{0} National ID already used').format(self.custom_nat_id))
        
    sync_user(self)
    self.role_profile_name = "Job Seeker"
    if self.new_password != "":
        user_doc = frappe.get_doc("User",self.name)
        user_doc.new_password = self.get_password('new_password')
        user_doc.save(ignore_permissions=True)
        self.new_password = ""
        
def permission_query(job_seeking_users):
    if frappe.session.user == "Administrator":
        return """`tabJob Seeking Users`.user_type = "Website User" """.format(job_seeking_users=job_seeking_users)
    else:
        return """`tabJob Seeking Users`.user_type = "Website User" """.format(job_seeking_users=job_seeking_users)

def sync_user(doc):
    user = frappe.get_doc("User", doc.name)
    
    fields_to_sync = frappe.get_meta("Job Seeking Users").fields

    for field in fields_to_sync:
        if field.fieldtype not in ["Section Break", "Column Break","HTML"]:
            if not field.fieldname.startswith("_") and not field.read_only:
                setattr(user, field.fieldname, getattr(doc, field.fieldname))

    user.save(ignore_permissions=True)

