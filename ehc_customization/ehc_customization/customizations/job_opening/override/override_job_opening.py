import frappe
from frappe import _
from frappe.model.naming import set_name_from_naming_options
from frappe.utils import get_link_to_form, getdate, pretty_date
from frappe.website.website_generator import WebsiteGenerator

class JobOpeningOverride(WebsiteGenerator):
    website = frappe._dict(
        template="templates/generators/job_opening.html",
        condition_field="publish",
        page_title_field="job_title",
    )
    website = frappe._dict(
        template="templates/generators/job_opening.html",
        condition_field="custom_publish_internal",
        page_title_field="job_title",
    )

    def get_context(self, context):
        all_internal_jobs_title = _("All Internal Jobs")
        all_jobs_title = _("All Jobs")
        if self.custom_publish_internal == "1":
            context.no_of_applications = frappe.db.count("Job Applicant", {"job_title": self.name})
            context.parents = [{"route": "internal_jobs", "title": all_internal_jobs_title}]
            context.posted_on = pretty_date(self.posted_on)
        if self.publish == "1":
            context.no_of_applications = frappe.db.count("Job Applicant", {"job_title": self.name})
            context.parents = [{"route": "jobs", "title": all_jobs_title}]
            context.posted_on = pretty_date(self.posted_on)
            


