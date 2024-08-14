import frappe
from frappe.desk.form import assign_to
import json

def do_assignment(self):
    assign_to.clear(self.doctype, self.name, ignore_permissions=True)


    if self.workflow_state == "Draft":
        if self.custom_ehc_evaluator:
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_ehc_evaluator:
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
            
                

    elif self.workflow_state == "New" or self.workflow_state == "In Progress" or self.workflow_state == "Investigator Assigned":
        if self.custom_ehc_validator :
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_ehc_validator:
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
                
    elif self.workflow_state == "Pending for Approval":
        if self.custom_ehc_investigator:
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_ehc_investigator:
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
                


    elif self.workflow_state == "Approved":
        if self.custom_ehc_approver:
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_ehc_approver:
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
                
             

    elif self.workflow_state == "Returned for Correction":
        if self.custom_network_representative:
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_network_representative: 
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
                
    elif self.workflow_state == "Read":
        if self.custom_facility_representative_new:
            shared_users = frappe.share.get_users(self.doctype, self.name)
            for user in shared_users:
                frappe.share.remove(self.doctype, self.name, user.user)
            for user in self.custom_facility_representative_new:
                assign_to.add(
                    dict(
                        assign_to=[user.name1],
                        doctype=self.doctype,
                        name=self.name,
                    ),
                    ignore_permissions=True,
                )
                
    elif self.workflow_state == "Close":
        assign_to.clear(self.doctype, self.name, ignore_permissions=True)
        shared_users = frappe.share.get_users(self.doctype, self.name)
        for user in shared_users:
            frappe.share.remove(self.doctype, self.name, user.user)
@frappe.whitelist()     
def get_user_role(doctype, txt, searchfield, start, page_len,role):
    ehcrole = role.get('role')
    ehc_validators = frappe.get_all("Has Role", {"role": ehcrole,"parenttype":"User"},['parent'])
    return [(role['parent'],) for role in ehc_validators]
