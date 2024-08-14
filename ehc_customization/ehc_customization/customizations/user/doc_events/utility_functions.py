import frappe
from frappe import _

def fetch_signup_data(self):
    user = frappe.get_doc("User",frappe.session.user)
    if user.user_type != "System User":
        if not frappe.db.exists("Job Seeking Users", {"user": self.name}):
            job_seeker = frappe.new_doc("Job Seeking Users")
            for field in self.meta.fields:
                if field.fieldname not in ["name", "creation", "modified"]:
                    job_seeker.set(field.fieldname, self.get(field.fieldname))
            try:
                job_seeker.role_profile_name = "Job Seeker"
                job_seeker.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error inserting Job Seeking Users {self.name}: {e}")

def validate_website_users(self):
    if not frappe.db.exists("Job Seeking Users", {"user": self.name}):
        job_seeker = frappe.new_doc("Job Seeking Users")
        for field in self.meta.fields:
            if field.fieldname not in ["name", "creation", "modified"]:
                job_seeker.set(field.fieldname, self.get(field.fieldname))
        try:
            job_seeker.role_profile_name = "Job Seeker"
            job_seeker.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error inserting Job Seeking Users {self.name}: {e}")

def permission_query(user):
    if frappe.session.user == "Administrator":
        return """`tabUser`.user_type = "System User" """.format(user=user)
    else:
        return """`tabUser`.user_type = "System User" """.format(user=user)