frappe.ui.form.on('Additional Salary', {
    refresh: function (frm) {
        if (frm.doc.custom_salay_slip && frm.doc.custom_payroll_entry) {
            frm.doc.custom_paid_additional_salary = 1
        }
        else {
            frm.doc.custom_paid_additional_salary = 0

        }

    },
})