frappe.ui.form.on("Payroll Entry",{
    payroll_structure: function (frm) {
		frm.events.clear_employee_table(frm);
	},
    clear_employee_table: function (frm) {
		frm.clear_table('employees');
		frm.refresh();
	},
    setup: function (frm) {

		frm.set_query('employee', 'employees', () => {
			let error_fields = [];
			let mandatory_fields = ['company', 'payroll_frequency', 'start_date', 'end_date'];

			let message = __('Mandatory fields required in {0}', [__(frm.doc.doctype)]);

			mandatory_fields.forEach(field => {
				if (!frm.doc[field]) {
					error_fields.push(frappe.unscrub(field));
				}
			});

			if (error_fields && error_fields.length) {
				message = message + '<br><br><ul><li>' + error_fields.join('</li><li>') + "</ul>";
				frappe.throw({
					message: message,
					indicator: 'red',
					title: __('Missing Fields')
				});
			}

			return {
				query: "hrms.payroll.doctype.payroll_entry.payroll_entry.employee_query",
				filters: frm.events.get_employee_filters(frm)
			};
		});
	},

	get_employee_filters: function (frm) {
		let filters = {};

		let fields = ['company', 'start_date', 'end_date', 'payroll_frequency', 'payroll_payable_account',
			'currency', 'department', 'branch', 'designation','payroll_structure', 'salary_slip_based_on_timesheet'];

		fields.forEach(field => {
			if (frm.doc[field] || frm.doc[field] === 0) {
				filters[field] = frm.doc[field];
			}
		});

		if (frm.doc.employees) {
			let employees = frm.doc.employees.filter(d => d.employee).map(d => d.employee);
			if (employees && employees.length) {
				filters['employees'] = employees;
			}
		}
		return filters;
	},
})