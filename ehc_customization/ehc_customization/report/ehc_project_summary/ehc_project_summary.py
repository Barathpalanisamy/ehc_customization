# Copyright (c) 2024, 8848digital and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = []

    data = frappe.db.get_all(
        "Project",
        filters=filters,
        fields=[
            "name",
            "project_name",
            "department",
            "status",
            "percent_complete",
            "expected_start_date",
            "expected_end_date",
            "project_type",
        ],
        order_by="expected_end_date",
    )

    for project in data:
        project["total_tasks"] = frappe.db.count("Task", filters={"project": project.name})
        project["completed_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "status": "Completed"}
        )
        project["overdue_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "status": "Overdue"}
        )
        project["in_progress_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "status": "Working"}
        )
        project["upcoming_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "status": "Open"}
        )

    chart = get_chart_data(data)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "fieldname": "project_name",
            "label": _("Project Name"),
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "project_type",
            "label": _("Type"),
            "fieldtype": "Link",
            "options": "Project Type",
            "width": 120,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 120,
        },
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_tasks", "label": _("Total Tasks"), "fieldtype": "Data", "width": 120},
        {
			"fieldname": "completed_tasks",
			"label": _("Tasks Completed"),
			"fieldtype": "Data",
			"width": 120,
		},
		{"fieldname": "overdue_tasks", "label": _("Tasks Overdue"), "fieldtype": "Data", "width": 120},
        {"fieldname": "percent_complete", "label": _("Completion"), "fieldtype": "Data", "width": 120},
        {
            "fieldname": "expected_start_date",
            "label": _("Start Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {"fieldname": "expected_end_date", "label": _("End Date"), "fieldtype": "Date", "width": 120},
    ]


def get_chart_data(data):
    labels = []
    total = []
    completed = []
    overdue = []
    in_progress = []
    upcoming = []

    for project in data:
        labels.append(project.project_name)
        total.append(project.total_tasks)
        completed.append(project.completed_tasks)
        overdue.append(project.overdue_tasks)
        in_progress.append(project.in_progress_tasks)
        upcoming.append(project.upcoming_tasks)

    return {
        "data": {
            "labels": labels[:30],
            "datasets": [
                {"name": _("In Progress"), "values": in_progress[:30]},
                {"name": _("Upcoming"), "values": upcoming[:30]},
                {"name": _("Overdue"), "values": overdue[:30]},
                {"name": _("Completed"), "values": completed[:30]},
                {"name": _("Total Tasks"), "values": total[:30]},
            ],
        },
        "type": "bar",
        "colors": ["#a9d4c0","#d8d8d8","#ffc000","#06A9AC","#3e9fda"],
        "barOptions": {"stacked": True},
    }


def get_report_summary(data):
    if not data:
        return None

    # avg_completion = sum(project.percent_complete for project in data) / len(data)
    total = sum([project.total_tasks for project in data])
    total_overdue = sum([project.overdue_tasks for project in data])
    completed = sum([project.completed_tasks for project in data])
    act_progress = (completed/total) * 100 if completed > 0 else 0
    # in_progress = sum([project.in_progress_tasks for project in data])
    # upcoming = sum([project.upcoming_tasks for project in data])

    return [
        {
            "value": act_progress,
            "indicator": "Green" if act_progress > 50 else "Red",
            "label": _("Completion Percentage"),
            "datatype": "Percent",
        },
        {
            "value": total,
            "indicator": "Blue",
            "label": _("Total Tasks"),
            "datatype": "Int",
        },
        {
            "value": completed,
            "indicator": "Green",
            "label": _("Completed Tasks"),
            "datatype": "Int",
        },
        {
            "value": total_overdue,
            "indicator": "Red" if total_overdue == 0 else "Red",
            "label": _("Overdue Tasks"),
            "datatype": "Int",
        },
    ]

