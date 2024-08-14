# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

import erpnext

def execute(filters=None):
    if not filters:
        filters = {}

    currency = None
    group_by_sc=False
    if filters.get("currency"):
        currency = filters.get("currency")
    company_currency = erpnext.get_company_currency(filters.get("company"))

    if filters.get("group_by_salary_component"):
        group_by_sc=True

    salary_slips = get_salary_slips(filters, company_currency)
    if not salary_slips:
        return [], []

    earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
    columns = get_columns(group_by_sc,earning_types,ded_types)
    
    ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
    ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

    if group_by_sc:
        ss_component_map = {}

        for slip_id, earning_details in ss_earning_map.items():
            ss_component_map[slip_id] = earning_details.copy()

        for slip_id, deduction_details in ss_ded_map.items():
            if slip_id in ss_component_map:
                ss_component_map[slip_id].update(deduction_details)
            else:
                ss_component_map[slip_id] = deduction_details.copy()

    

    doj_map = get_employee_doj_map()

    data = []
    for ss in salary_slips:
        # accounting_department = list(set(doj_map.get(ss.name, {}).get("accounting_department", [])))
        row = {
            "salary_slip_id": ss.name,
            "employee": ss.employee,
            "employee_name": ss.employee_name,
            "data_of_joining": doj_map.get(ss.employee),
            "branch": ss.branch,
            "department": ss.department,
            "designation": ss.designation,
            "company": ss.company,
            "start_date": ss.start_date,
            "end_date": ss.end_date,
            "leave_without_pay": ss.leave_without_pay,
            "payment_days": ss.payment_days,
            "currency": currency or company_currency,
            "total_loan_repayment": ss.total_loan_repayment,
        }

        update_column_width(ss, columns)

        if group_by_sc:
            data.append(row)
            all_types = earning_types + ded_types
            for component in all_types:
                amount = ss_component_map.get(ss.name, {}).get(component)
                data.append({"salary_component": component, "salary_component_amount": amount})
            
            if currency == company_currency:
                data.append(
                    {
                        "gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
                        "total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
                        "net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
                    }
                )

            else:
                data.append(
                    {"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
                )
        else:
            for e in earning_types:
                row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})

            for d in ded_types:
                row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})

            if currency == company_currency:
                row.update(
                    {
                        "gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
                        "total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
                        "net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
                    }
                )

            else:
                row.update(
                    {"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
                )

        
            data.append(row)
    
    return columns, data


def get_earning_and_deduction_types(salary_slips):
    salary_component_and_type = {_("Earning"): [], _("Deduction"): []}

    for salary_compoent in get_salary_components(salary_slips):
        component_type = get_salary_component_type(salary_compoent)
        salary_component_and_type[_(component_type)].append(salary_compoent)

    return sorted(salary_component_and_type[_("Earning")]), sorted(
        salary_component_and_type[_("Deduction")]
    )


def update_column_width(ss, columns):
    if ss.branch is not None:
        columns[3].update({"width": 120})
    if ss.department is not None:
        columns[4].update({"width": 120})
    if ss.designation is not None:
        columns[5].update({"width": 120})
    if ss.leave_without_pay is not None:
        columns[9].update({"width": 120})


def get_columns(group_by_sc,earning_types=None,ded_types=None):
    columns = [
        {
            "label": _("Salary Slip ID"),
            "fieldname": "salary_slip_id",
            "fieldtype": "Link",
            "options": "Salary Slip",
            "width": 150,
        },
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Date of Joining"),
            "fieldname": "data_of_joining",
            "fieldtype": "Date",
            "width": 80,
        },
        {
            "label": _("Branch"),
            "fieldname": "branch",
            "fieldtype": "Link",
            "options": "Branch",
            "width": -1,
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": -1,
        },
        {
            "label": _("Designation"),
            "fieldname": "designation",
            "fieldtype": "Link",
            "options": "Designation",
            "width": 120,
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 120,
        },
        {
            "label": _("Start Date"),
            "fieldname": "start_date",
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "label": _("End Date"),
            "fieldname": "end_date",
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "label": _("Leave Without Pay"),
            "fieldname": "leave_without_pay",
            "fieldtype": "Float",
            "width": 50,
        },
        {
            "label": _("Payment Days"),
            "fieldname": "payment_days",
            "fieldtype": "Float",
            "width": 120,
        },
    ]

    if group_by_sc:
        columns.extend([
        
            {
                "label": _("Salary Component"),
                "fieldname": "salary_component",
                "fieldtype": "Link",
                "options": "Salary Component",
                "width": 120,
            },
            {
                "label":_("Salary Component Value"),
                "fieldname": "salary_component_amount",
                "fieldtype": "Link",
                "options": "Salary Component",
                "width": 120,
            },
            {
                "label": _("Gross Pay"),
                "fieldname": "gross_pay",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            ]
        )
    else:
        for earning in earning_types:
            columns.append(
                {
                    "label": earning,
                    "fieldname": frappe.scrub(earning),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )

        columns.append(
            {
                "label": _("Gross Pay"),
                "fieldname": "gross_pay",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            }
        )

        for deduction in ded_types:
            columns.append(
                {
                    "label": deduction,
                    "fieldname": frappe.scrub(deduction),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )

        
    
    columns.extend(
        [
            
            {
                "label": _("Total Deduction"),
                "fieldname": "total_deduction",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Loan Repayment"),
                "fieldname": "total_loan_repayment",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Net Pay"),
                "fieldname": "net_pay",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Currency"),
                "fieldtype": "Data",
                "fieldname": "currency",
                "options": "Currency",
                "hidden": 1,
            },
        ]
    )
    return columns


def get_salary_components(salary_slips):
    salary_detail = frappe.qb.DocType("Salary Detail")

    return (
        frappe.qb.from_(salary_detail)
        .where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
        .select(salary_detail.salary_component)
        .distinct()
        .orderby(salary_detail.salary_component)
    ).run(pluck=True)


def get_salary_component_type(salary_component):
    return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
    salary_slip = frappe.qb.DocType("Salary Slip")
    employee = frappe.qb.DocType("Employee")
    
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    query = (
            frappe.qb.from_(salary_slip)
            .select(salary_slip.star)
            .join(employee)
            .on(salary_slip.employee_name == employee.employee_name)
        )
    # query = frappe.qb.from_(salary_slip).select(salary_slip.star)

    if filters.get("docstatus"):
        query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

    if filters.get("from_date"):
        query = query.where(salary_slip.start_date >= filters.get("from_date"))

    if filters.get("to_date"):
        query = query.where(salary_slip.end_date <= filters.get("to_date"))

    if filters.get("company"):
        query = query.where(salary_slip.company == filters.get("company"))

    if filters.get("employee"):
        query = query.where(salary_slip.employee == filters.get("employee"))

    if filters.get("currency") and filters.get("currency") != company_currency:
        query = query.where(salary_slip.currency == filters.get("currency"))
    
    if filters.get("accounting_department"):
        query = query.where(salary_slip.ehc_accounting_department.isin(filters.get("accounting_department")))
    
    if filters.get("branch"):
        query = query.where(salary_slip.branch == filters.get("branch"))

    if filters.get("designation"):
        query = query.where(salary_slip.designation == filters.get("designation"))

    if filters.get("department"):
        query = query.where(salary_slip.department == filters.get("department"))
    
    if filters.get("financial_job_category"):
        query = query.where(employee.financial_job_category == filters.get("financial_job_category"))

    if filters.get("nationality_group"):
        query = query.where(employee.nationality_group == filters.get("nationality_group"))

    if filters.get("cost_center"):
        query = query.where(salary_slip.ehc_cost_center.isin(filters.get("cost_center")))

    
    salary_slips = query.run(as_dict=1)

    return salary_slips or []

def get_employee_doj_map():
	employee = frappe.qb.DocType("Employee")

	result = (frappe.qb.from_(employee).select(employee.name, employee.date_of_joining)).run()

	return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, component_type):
    salary_slip = frappe.qb.DocType("Salary Slip")
    salary_detail = frappe.qb.DocType("Salary Detail")
    salary_slips = [ss.name for ss in salary_slips]

    result = (
        frappe.qb.from_(salary_slip)
        .join(salary_detail)
        .on(salary_slip.name == salary_detail.parent)
        .where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == component_type))
        .select(
            salary_detail.parent,
            salary_detail.salary_component,
            salary_detail.amount,
            salary_slip.exchange_rate,
        )
    ).run(as_dict=1)

    ss_map = {}

    for d in result:
        ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
        if currency == company_currency:
            ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
                d.exchange_rate if d.exchange_rate else 1
            )
        else:
            ss_map[d.parent][d.salary_component] += flt(d.amount)

    return ss_map