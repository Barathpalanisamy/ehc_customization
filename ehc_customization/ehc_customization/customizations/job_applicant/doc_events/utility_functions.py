import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import add_to_date, cast, nowdate, validate_email_address
from frappe.utils.safe_exec import get_safe_globals
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification

def send_notification_for_new_job_appicant(self):
    if not self.get("status") == "Open":
        return
    users=[]
    jobs = frappe.get_all(
        "Job Opening",
        filters={"name": self.job_title},
        fields=["name", "job_category"]
    )
    for job in jobs:
        employees = frappe.get_all(
            "Employee",
            filters={"job_category": job.job_category},
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