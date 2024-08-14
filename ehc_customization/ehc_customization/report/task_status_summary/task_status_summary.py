
import frappe
from frappe import _

def execute(filters=None):
    # Fetch all unique status types
    status_types = frappe.db.get_list("Task", distinct=True, fields=["status"])
    status_types = [status_type.get("status") for status_type in status_types]

    columns = get_columns(status_types)
    data = []

    # Fetch project data
    projects = frappe.db.get_all(
        "Project",
        filters=filters,
        fields=[
            "name",
            "status",
            "project_name",
            "percent_complete",
            "expected_start_date",
            "expected_end_date",
            "project_type",
        ],
        order_by="expected_end_date",
    )

    for project in projects:
        # Initialize project task counts
        project_data = {
            "name": project.name,
            "project_name": project.project_name,
            "status": project.status,
            "percent_complete": project.percent_complete,
            "expected_start_date": project.expected_start_date,
            "expected_end_date": project.expected_end_date,
            "project_type": project.project_type,
            "total_tasks": 0
        }

        # Fetch task counts for each status type
        for status in status_types:
            count = frappe.db.count("Task", filters={"project": project.name, "status": status})
            project_data[f"{status.lower()}_tasks"] = count
            project_data["total_tasks"] += count

        data.append(project_data)

    chart = get_chart_data(data, status_types)
    report_summary = get_report_summary(data, status_types)

    return columns, data, None, chart, report_summary

def get_columns(status_types):
    columns = [
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
        {"fieldname": "percent_complete", "label": _("Completion"), "fieldtype": "Data", "width": 120},
        {
            "fieldname": "expected_start_date",
            "label": _("Start Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {"fieldname": "expected_end_date", "label": _("End Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "total_tasks", "label": _("Total Tasks"), "fieldtype": "Data", "width": 120},
    ]

    for status in status_types:
        columns.append({"fieldname": f"{status.lower()}_tasks", "label": _(status), "fieldtype": "Data", "width": 120})

    return columns

def get_chart_data(data, status_types):
    labels = [project["project_name"] for project in data]
    datasets = []

    for status in status_types:
        dataset = {
            "name": _(status),
            "values": [project.get(f"{status.lower()}_tasks", 0) for project in data]
        }
        datasets.append(dataset)

    return {
        "data": {
            "labels": labels[:30],
            "datasets": datasets[:30],
        },
        "type": "bar",
        "colors": ["#fc4f51", "#78d6ff", "#7575ff"],  # Adjust colors as needed
        "barOptions": {"stacked": True},
    }

def get_report_summary(data, status_types):
    if not data:
        return None

    avg_completion = sum(project["percent_complete"] for project in data if project["percent_complete"]) / len(data)
    total_tasks = sum(project["total_tasks"] for project in data if project["total_tasks"])

    summary = [
        {
            "value": avg_completion,
            "indicator": "Green" if avg_completion > 50 else "Red",
            "label": _("Average Completion"),
            "datatype": "Percent",
        },
        {
            "value": total_tasks,
            "indicator": "Blue",
            "label": _("Total Tasks"),
            "datatype": "Int",
        },
    ]

    # Add summary for each status type
    for status in status_types:
        status_tasks = sum(project.get(f"{status.lower()}_tasks", 0) for project in data)
        summary.append({
            "value": status_tasks,
            "indicator": "Green",
            "label": _(f"{status} Tasks"),
            "datatype": "Int",
        })

    return summary
