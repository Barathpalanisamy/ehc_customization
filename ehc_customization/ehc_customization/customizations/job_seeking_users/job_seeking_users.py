import frappe
from ehc_customization.ehc_customization.customizations.job_seeking_users.api.utility_functions import (
	update_password
)

# @frappe.whitelist()    
# def assign_roles(user,profile):
#     add_roles_to_user(user,profile)
    
@frappe.whitelist()    
def validate(self, method=None):
    update_password(self)