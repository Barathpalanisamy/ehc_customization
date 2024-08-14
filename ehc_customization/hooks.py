from . import __version__ as app_version

app_name = "ehc_customization"
app_title = "Ehc Customizations"
app_publisher = "8848digital"
app_description = "EHC"
app_email = "developer@8848digital.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ehc_customization/css/ehc_customization.css"
app_include_js = ["ehc_hierarchy_chart.bundle.js", "/assets/ehc_customization/js/job_opening_notification.js"]

# include js, css files in header of web template
# web_include_css = "/assets/ehc_customization/css/ehc_customization.css"
# web_include_js = "/assets/ehc_customization/js/ehc_customization.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ehc_customization/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

after_migrate = "ehc_customization.migrate.after_migrate"
# include js in doctype views

doctype_js = {
    "Material Request": "ehc_customization/customizations/material_request/material_request.js",
    "Pick List": "ehc_customization/customizations/pick_list/pick_list.js",
    "Sales Invoice": "ehc_customization/customizations/sales_invoice/sales_invoice.js",
    "Purchase Invoice": "ehc_customization/customizations/purchase_invoice/purchase_invoice.js",
    "Job Applicant": "ehc_customization/customizations/job_applicant/job_applicant.js",
    "Journal Entry": "ehc_customization/customizations/journal_entry/journal_entry.js",
    "Stock Entry": "ehc_customization/customizations/stock_entry/stock_entry.js",
    "Payroll Entry": "ehc_customization/customizations/payroll_entry/payroll_entry.js",
    "Budget": "ehc_customization/customizations/budget/budget.js",
    "Budget Transfer": "ehc_customization/customizations/budget_transfer/budget_transfer.js",
    "Job Opening": "ehc_customization/customizations/job_opening/job_opening.js",
    "Employee":"ehc_customization/customizations/employee/employee.js",
    "Purchase Order": "ehc_customization/customizations/purchase_order/purchase_order.js",
    "Purchase Receipt": "ehc_customization/customizations/purchase_receipt/purchase_receipt.js",
    "Supplier Quotation": "ehc_customization/customizations/supplier_quotation/supplier_quotation.js",
    "Payment Entry": "ehc_customization/customizations/payment_entry/payment_entry.js",
    "Expense Claim": "ehc_customization/customizations/expense_claim/expense_claim.js",
    "Skill Assessment": "ehc_customization/customizations/skill_assessment/skill_assessment.js",
    "Attendance Request": "ehc_customization/customizations/attendance_request/attendance_request.js",
    "Interview Feedback": "ehc_customization/customizations/interview_feedback/interview_feedback.js",
    "Attendance": "ehc_customization/customizations/attendance/attendance.js",
    "User": "ehc_customization/customizations/user/user.js",
    "Designation":"ehc_customization/customizations/designation/designation.js",
    "Department":"ehc_customization/customizations/department/department.js",
    "Job Seeking Users":"ehc_customization/customizations/job_seeking_users/job_seeking_users.js",
    "Additional Salary":"ehc_customization/customizations/additional_salary/additional_salary.js",
    "Employee Checkin":"ehc_customization/customizations/employee_checkin/employee_checkin.js",
    "Interview":"ehc_customization/customizations/interview/interview.js",
    "Quality Inspection":"ehc_customization/customizations/quality_inspection/quality_inspection.js"
}
# doctype_list_js = {"Monthly Time Allocation" : "ehc_customization/customizations/monthly_time_allocation/monthly_time_allocation_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ehc_customization.utils.jinja_methods",
# 	"filters": "ehc_customization.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ehc_customization.install.before_install"
# after_install = "ehc_customization.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ehc_customization.uninstall.before_uninstall"
# after_uninstall = "ehc_customization.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ehc_customization.utils.before_app_install"
# after_app_install = "ehc_customization.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ehc_customization.utils.before_app_uninstall"
# after_app_uninstall = "ehc_customization.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ehc_customization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways
permission_query_conditions = {
	"User":"ehc_customization.ehc_customization.customizations.user.doc_events.utility_functions.permission_query",
    "Attendance Request": "ehc_customization.ehc_customization.customizations.attendance_request.permission.permission_query.reports_to",
    "Employee Checkin": "ehc_customization.ehc_customization.customizations.employee_checkin.permission.permission_query.reports_to",
    "Violation Request": "ehc_customization.ehc_customization.doctype.violation_request.permission.permission_query.reports_to",
    "Job Seeking Users":"ehc_customization.ehc_customization.customizations.job_seeking_users.api.utility_functions.permission_query"
}
# permission_query_conditions = {
# 	# "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# 	"Users Access Control":"ehc_customization.ehc_customization.doc_events.material_request.get_roles"
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {

    "Appraisal": "ehc_customization.ehc_customization.customizations.appraisal.appraisal.AppraisalCalculation",
    "Payroll Entry": "ehc_customization.ehc_customization.customizations.payroll_entry.payroll_entry.payrollentryoverride",
    "Budget":"ehc_customization.ehc_customization.customizations.budget.budget.BudgetOverride",
    "Salary Slip":"ehc_customization.ehc_customization.customizations.salary_slip.salary_slip.salaryslip_override",
    "Attendance Request": "ehc_customization.ehc_customization.customizations.attendance_request.attendance_request.AttendanceRequestCreation",
    "Shift Type": "ehc_customization.ehc_customization.customizations.shift_type.shift_type.OverrideShiftType",
    "Data Import": "ehc_customization.ehc_customization.customizations.data_import.data_import.DataImportMerge",
    "Job Opening":"ehc_customization.ehc_customization.customizations.job_opening.override.override_job_opening.JobOpeningOverride",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Pick List": {
        "validate": "ehc_customization.ehc_customization.customizations.pick_list.pick_list.validate",
        "on_cancel": "ehc_customization.ehc_customization.customizations.pick_list.pick_list.on_cancel",
    },
    "Stock Entry": {
        "on_submit": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.on_submit",
        "on_cancel": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.on_cancel",
        "validate": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.stock_entry.stock_entry.on_cancel",
    },
    "Material Request": {
        "validate": "ehc_customization.ehc_customization.customizations.material_request.material_request.validate",
        "on_submit": "ehc_customization.ehc_customization.customizations.material_request.material_request.on_submit",
        "after_insert": "ehc_customization.ehc_customization.customizations.material_request.material_request.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.material_request.material_request.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.material_request.material_request.on_cancel",

    },
     "Job Opening": {
        "after_insert": "ehc_customization.ehc_customization.customizations.job_opening.job_opening.after_save"
    },
    "Job Applicant": {
        "after_insert": "ehc_customization.ehc_customization.customizations.job_applicant.job_applicant.after_save"
    },
    "Employee":{
        "validate": "ehc_customization.ehc_customization.customizations.employee.employee.after_save",
        "after_insert": "ehc_customization.ehc_customization.customizations.employee.employee.insert_after",
        "on_update" : "ehc_customization.ehc_customization.customizations.employee.employee.update",
        "on_trash" : "ehc_customization.ehc_customization.customizations.employee.employee.delete",
    },
    "Designation": {
        "after_insert": "ehc_customization.ehc_customization.customizations.designation.designation.insert_after",
        "on_update" : "ehc_customization.ehc_customization.customizations.designation.designation.update",
        "on_trash" : "ehc_customization.ehc_customization.customizations.designation.designation.delete",
	},
    "Department": {
        "after_insert": "ehc_customization.ehc_customization.customizations.department.department.insert_after",
        "on_update" : "ehc_customization.ehc_customization.customizations.department.department.update",
        "on_trash" : "ehc_customization.ehc_customization.customizations.department.department.delete",
	},
    "Sales Invoice":{
        "on_submit": "ehc_customization.ehc_customization.customizations.sales_invoice.sales_invoice.on_submit",
        "validate": "ehc_customization.ehc_customization.customizations.sales_invoice.sales_invoice.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.sales_invoice.sales_invoice.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.sales_invoice.sales_invoice.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.sales_invoice.sales_invoice.on_cancel",

    },
    "Purchase Invoice":{
        "on_submit": "ehc_customization.ehc_customization.customizations.purchase_invoice.purchase_invoice.on_submit",
        "validate": "ehc_customization.ehc_customization.customizations.purchase_invoice.purchase_invoice.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.purchase_invoice.purchase_invoice.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.purchase_invoice.purchase_invoice.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.purchase_invoice.purchase_invoice.on_cancel",

    },
    "Journal Entry":{
        "on_submit": "ehc_customization.ehc_customization.customizations.journal_entry.journal_entry.on_submit",
        "validate": "ehc_customization.ehc_customization.customizations.journal_entry.journal_entry.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.journal_entry.journal_entry.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.journal_entry.journal_entry.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.journal_entry.journal_entry.on_cancel",

    },
    "Stock Reconciliation":{
        "on_submit": "ehc_customization.ehc_customization.customizations.stock_reconciliation.stock_reconciliation.on_submit",
        "validate": "ehc_customization.ehc_customization.customizations.stock_reconciliation.stock_reconciliation.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.stock_reconciliation.stock_reconciliation.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.stock_reconciliation.stock_reconciliation.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.stock_reconciliation.stock_reconciliation.on_cancel",

    },
    "Expense Claim":{
        "on_submit": "ehc_customization.ehc_customization.customizations.expense_claim.expense_claim.on_submit",
        "validate": "ehc_customization.ehc_customization.customizations.expense_claim.expense_claim.validate",
        "after_insert": "ehc_customization.ehc_customization.customizations.expense_claim.expense_claim.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.expense_claim.expense_claim.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.expense_claim.expense_claim.on_cancel",

    },
    "Purchase Order":{
        "validate": "ehc_customization.ehc_customization.customizations.purchase_order.purchase_order.validate",
        "on_submit": "ehc_customization.ehc_customization.customizations.purchase_order.purchase_order.on_submit",
        "after_insert": "ehc_customization.ehc_customization.customizations.purchase_order.purchase_order.after_save",
        "on_update": "ehc_customization.ehc_customization.customizations.purchase_order.purchase_order.on_update",
        "on_trash": "ehc_customization.ehc_customization.customizations.purchase_order.purchase_order.on_cancel",

    } ,
    "Budget Transfer": {
        "on_submit": "ehc_customization.ehc_customization.customizations.budget_transfer.budget_transfer.on_submit",
        "on_cancel": "ehc_customization.ehc_customization.customizations.budget_transfer.budget_transfer.on_cancel"
    },
     "User": {
        "after_insert": "ehc_customization.ehc_customization.customizations.user.user.after_save"
    },
     "Salary Slip":{
        "validate":"ehc_customization.ehc_customization.customizations.salary_slip.salary_slip.validate",
        "on_submit":"ehc_customization.ehc_customization.customizations.salary_slip.salary_slip.on_submit",
        "on_cancel":"ehc_customization.ehc_customization.customizations.salary_slip.salary_slip.on_cancel"
    },
    # "Department":{
    #     "validate":"ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions.validate"
    # },
    "Scholarship":{
        "validate": "ehc_customization.ehc_customization.doctype.scholarship.doc_events.utility_function.validate"
    },
    "Violation Request":{
        "validate": "ehc_customization.ehc_customization.doctype.violation_request.api.api.validate"
    },
    "Attendance Deduction":{
        "validate": "ehc_customization.ehc_customization.doctype.attendance_deduction.api.utility.validate"
    },
    "Permission Policy Assignment":{
        "validate": "ehc_customization.ehc_customization.doctype.permission_policy_assignment.doc_events.utility.validate"
    },
    "Payroll Entry":{
        "on_cancel":"ehc_customization.ehc_customization.customizations.payroll_entry.payroll_entry.on_cancel"
    },
    "Quality Inspection":{
        "on_update":"ehc_customization.ehc_customization.customizations.quality_inspection.quality_inspection.on_update"
    },
    "Job Seeking Users":{
        "validate": "ehc_customization.ehc_customization.customizations.job_seeking_users.job_seeking_users.validate"
    },
    "Interview Feedback":{
        "on_submit": "ehc_customization.ehc_customization.customizations.interview_feedback.doc_events.utility_functions.on_submit"
    },
    "Branch": {
        "after_insert": "ehc_customization.ehc_customization.customizations.branch.branch.insert_after",
        "on_update" : "ehc_customization.ehc_customization.customizations.branch.branch.update",
        "on_trash" : "ehc_customization.ehc_customization.customizations.branch.branch.delete",
    },
    "LMS Scheduler Settings": {
        "validate": "ehc_customization.ehc_customization.doctype.lms_scheduler_settings.lms_scheduler_settings.validate"
    },
     "ToDo": {
        "after_insert": "ehc_customization.ehc_customization.customizations.todo.todo.insert_after",
        "on_update" : "ehc_customization.ehc_customization.customizations.todo.todo.update",
        "on_trash" : "ehc_customization.ehc_customization.customizations.todo.todo.delete",
    },
    "File": {
        "after_insert": "ehc_customization.ehc_customization.customizations.file_list.file_list.insert_file",
        "on_trash" : "ehc_customization.ehc_customization.customizations.file_list.file_list.delete",
	},
    "Interview":{
        "on_update": "ehc_customization.ehc_customization.customizations.interview.doc_events.utility_functions.on_update"
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"ehc_customization.tasks.all"
# 	],
    "daily": [
        "ehc_customization.ehc_customization.customizations.job_opening.scheduler.update_status.update_status",
        "ehc_customization.ehc_customization.customizations.shift_type.scheduler.scheduler.trigger_attendance",
        "ehc_customization.ehc_customization.doctype.scholarship.scheduler.scheduler.update_end_status",
        "ehc_customization.ehc_customization.doctype.employee_delegation.scheduler.employee_delegation_scheduler.update_temporary_employee",
        "ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions.call_event_streaming",
        "ehc_customization.ehc_customization.customizations.department.doc_events.utility_functions.sync_between_servers"
    ],
# 	"hourly": [
# 		"ehc_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ehc_customization.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ehc_customization.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "ehc_customization.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ehc_customization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ehc_customization.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ehc_customization.utils.before_request"]
# after_request = ["ehc_customization.utils.after_request"]

# Job Events
# ----------
# before_job = ["ehc_customization.utils.before_job"]
# after_job = ["ehc_customization.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ehc_customization.auth.validate"
# ]

# fixtures = [
#         {"dt": "Custom Field", "filters": [
#                 [
#                     "name", "in", [
#                         "HR Settings-custom_scholarship_access_role",
#                     ]
#                ]
#     ]}
# ]

