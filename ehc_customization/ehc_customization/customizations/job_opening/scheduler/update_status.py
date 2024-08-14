from datetime import datetime
import frappe


def update_status():
    today = datetime.now().date()
    job_opening=frappe.get_all("Job Opening",{"status":["!=","Closed"]},pluck="name")
    if job_opening:
        for i in job_opening:

            from_date=frappe.db.get_value("Job Opening",i,"from_date")
            to_date=frappe.db.get_value("Job Opening",i,"to_date")

            if not from_date <= today <= to_date:
                frappe.db.set_value("Job Opening",i,"status","Closed")
                frappe.db.set_value("Job Opening",i,"publish",0)
