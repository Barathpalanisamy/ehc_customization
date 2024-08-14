frappe.ui.form.on("Employee", {
    reports_to: function (frm) {
        if (frm.doc.reports_to) {
            frappe.db.get_value(
                "Employee",
                {
                    name: frm.doc.reports_to,
                },
                "user_id",
                (r) => {
                    frm.set_value("expense_approver", r.user_id);
                    frm.set_value("leave_approver", r.user_id);
                    frm.set_value("shift_request_approver", r.user_id);
                }
            );
        }
        else {
            frm.set_value("expense_approver", "");
            frm.set_value("leave_approver", "");
            frm.set_value("shift_request_approver", "");

        }
    },
    department: function (frm) {
        if (frm.doc.department && frm.doc.manager_type == "Direct Manager") {
            frappe.db.get_value(
                "Department",
                {
                    name: frm.doc.department,
                },
                "custom_reports_to",
                (r) => {
                    frm.set_value("reports_to", r.custom_reports_to);

                }
            );
        }
    },
    manager_type:function(frm){
        if (frm.doc.department && frm.doc.manager_type == "Direct Manager") {
            frappe.db.get_value(
                "Department",
                {
                    name: frm.doc.department,
                },
                "custom_reports_to",
                (r) => {
                    frm.set_value("reports_to", r.custom_reports_to);

                }
            );
        }

    },
    payroll_cost_center: function (frm) {
        var cost_center = frm.doc.payroll_cost_center;
        frm.set_value('ehc_accounting_department', '');
        if (cost_center) {
            frm.set_query('ehc_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: cost_center
                    }
                };
            });
        }
    },
    onload_post_render: function (frm) {
        if (frm.doc.payroll_cost_center) {
            frm.set_query('ehc_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.payroll_cost_center
                    }
                };
            });
        }
    },
})
