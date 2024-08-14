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
        project["milestone_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "is_milestone": 1}
        )
        project["initiative_tasks"] = frappe.db.count(
            "Task", filters={"project": project.name, "custom_is_initiative": 1}
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
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_tasks", "label": _("Total Tasks"), "fieldtype": "Data", "width": 120},
        {
			"fieldname": "milestone_tasks",
			"label": _("Tasks Milestone"),
			"fieldtype": "Data",
			"width": 120,
		},
		{"fieldname": "initiative_tasks", "label": _("Tasks Initiative"), "fieldtype": "Data", "width": 120},
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
    milestone = []
    initiative = []

    for project in data:
        labels.append(project.project_name)
        total.append(project.total_tasks)
        milestone.append(project.milestone_tasks)
        initiative.append(project.initiative_tasks)

    return {
        "data": {
            "labels": labels[:30],
            "datasets": [
                {"name": _("Initiative"), "values": initiative[:30]},
                {"name": _("Milestone"), "values": milestone[:30]},
                {"name": _("Total Tasks"), "values": total[:30]},
            ],
        },
        "type": "bar",
        "colors": ["#fc4f51","#78d6ff","#7575ff"],
        "barOptions": {"stacked": True},
    }


def get_report_summary(data):
    if not data:
        return None

    avg_completion = sum(project.percent_complete for project in data) / len(data)
    total = sum([project.total_tasks for project in data])
    initiative = sum([project.initiative_tasks for project in data])
    milestone = sum([project.milestone_tasks for project in data])

    return [
        {
            "value": avg_completion,
            "indicator": "Green" if avg_completion > 50 else "Red",
            "label": _("Average Completion"),
            "datatype": "Percent",
        },
        {
            "value": total,
            "indicator": "Blue",
            "label": _("Total Tasks"),
            "datatype": "Int",
        },
        {
            "value": milestone,
            "indicator": "Green",
            "label": _("Milestone Tasks"),
            "datatype": "Int",
        },
        {
            "value": initiative,
            "indicator": "Red",
            "label": _("Initiative Tasks"),
            "datatype": "Int",
        },
    ]
