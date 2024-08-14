import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import add_to_date, cast, nowdate, validate_email_address
from frappe.utils.safe_exec import get_safe_globals
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
import difflib
import re

def send_notification_for_new_job_opening(self):
    if not self.get("status") == "Open":
        return
    users=[]
    if self.job_category:
        job_category = self.job_category
        employees = frappe.get_all(
            "Employee",
            filters={"job_category": job_category},
            fields=["name", "employee_name", "company_email"]
        )
        for employee in employees:
            employee_name = employee.employee_name
            email_id = employee.company_email
            users.append(email_id)
    else:
        employees = frappe.get_all(
            "Employee",
            fields=["name", "employee_name", "company_email"]
        )
        for employee in employees:
            employee_name = employee.employee_name
            email_id = employee.company_email
            users.append(email_id)
    
        
    if not users:
        return
    
    notification_name = "Job Opening"
    doc = frappe.get_doc("Notification", notification_name)
    context = get_context(self)
    subject = doc.subject
    if "{" in subject:
        subject = frappe.render_template(doc.subject, context)

    notification_doc = {
        "type": "Alert",
        "document_type": self.doctype,
        "document_name": self.name,
        "subject": subject,
        "from_user": self.modified_by or self.owner,
        "email_content": frappe.render_template(doc.message, context),
    }
    enqueue_create_notification(users, notification_doc)

def get_context(self):
    return {
        "doc": self,
        "nowdate": nowdate,
        "frappe": frappe._dict(utils=get_safe_globals().get("frappe").get("utils")),
    }

def validation_on_internal_route(self):
    if self.job_opening_category == "Internal":
        self.route_internal = f"internal_job/{frappe.scrub(self.company)}/{frappe.scrub(self.job_title).replace('_', '-')}"
        self.route = None

@frappe.whitelist(allow_guest=True)            
def fetch_doc_values(source_name,source,target):
    get_doc = frappe.get_doc('Job Profile Mapping', {'source':source,'target':target}, ['*'])
    get_data =frappe.get_all('Mapped Fields', fields=["target_fieldname","source_fieldname","source_fields","target_fields"], filters = dict(parent=get_doc.name))
    source_doc = frappe.get_doc(source,source_name)
    matched_fields_values = []
    for i in get_data:
        for field in source_doc.meta.fields:
            if field.fieldname == i.source_fieldname:
                field_value = source_doc.get(i.source_fieldname)
                if isinstance(field_value, list):
                    parent_value = extract_parent_value(field_value)
                    child_table = frappe.get_all(field.options, filters = dict(parent=parent_value),fields = ["*"])
                    matched_fields_values.append((i.target_fieldname,child_table))
                else:
                    matched_fields_values.append((i.target_fieldname,source_doc.get(i.source_fieldname)))
    return matched_fields_values

def extract_parent_value(obj):
    obj_string = str(obj)
    pattern = r'parent=([^\s>]+)'
    match = re.search(pattern, obj_string)
    
    if match:
        return match.group(1)
    else:
        return None

############################################## Mapping using Difflib Python Library ########################################################
# @frappe.whitelist(allow_guest=True)            
# def fetch_doc_values(name,source,target):
#     source = frappe.get_doc(source,name)
#     target = frappe.new_doc(target)
    
#     source_fields = [field.fieldname for field in source.meta.fields if source.meta.get_field(field.fieldname).fieldtype not in ['Column Break','Section Break']]
#     target_fields = [field.fieldname for field in target.meta.fields if target.meta.get_field(field.fieldname).fieldtype not in ['Column Break','Section Break']]
#     matched_fields_values = []
    
#     for field in target.meta.fields:
#         fieldtype = target.meta.get_field(field.fieldname).fieldtype
#         matched_field = difflib.get_close_matches(field.fieldname, source_fields, cutoff=0.6)
#         if not matched_field:
#             matched_field = difflib.get_close_matches(field.fieldname, source_fields, cutoff=0.5)
#         if matched_field:
#             if source.meta.get_field(matched_field[0]).fieldtype == fieldtype:
#                 if field.fieldname != matched_field[0] and matched_field[0] in target_fields:
#                     matched_field = ['']
#                 matched_value = source.get(matched_field[0])
#                 matched_fields_values.append((field.fieldname, matched_value))
                
#     return matched_fields_values