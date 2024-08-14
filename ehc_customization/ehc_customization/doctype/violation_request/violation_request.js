// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on('Violation Request', {
	onload(frm){
		frappe.db.get_value('Employee', frm.doc.employee, 'user_id')
		.then(ret => {
			console.log(ret, frappe.session.user)
			if(ret.message.user_id == frappe.session.user){
				frm.set_df_property('employee', 'read_only', 1);
				frm.set_df_property('status', 'read_only', 1);
				frm.set_df_property('late_count', 'read_only', 1);
				frm.set_df_property('late_hours', 'read_only', 1);
				frm.set_df_property('month', 'read_only', 1);
				frm.set_df_property('hr_details', 'read_only', 1);
				frm.set_df_property('employee_reason', 'reqd', 1);
				frm.set_df_property('transaction_date', 'read_only', 1);
				frm.set_df_property('naming_series', 'read_only', 1);
				frm.set_df_property('fiscal_year', 'read_only', 1);
				frm.set_df_property('late_entry_dates', 'read_only', 1);



			}
		})
		if(frm.doc.employee){
			// frm.trigger('employee')
			// frm.trigger('status')
			// if(frm.doc.docstatus == 0 && !frm.doc.__islocal){
			// 	frm.save()
			// }
			if((frm.doc.hr_details == frappe.session.user) || (frm.doc.attendance_team == frappe.session.user)){
				frm.set_df_property('employee', 'read_only', 1);
				frm.set_df_property('late_count', 'read_only', 1);
				frm.set_df_property('late_hours', 'read_only', 1);
				frm.set_df_property('month', 'read_only', 1);
				frm.set_df_property('hr_details', 'read_only', 1);
				frm.set_df_property('transaction_date', 'read_only', 1);
				frm.set_df_property('naming_series', 'read_only', 1);
				frm.set_df_property('fiscal_year', 'read_only', 1);
				frm.set_df_property('late_entry_dates', 'read_only', 1);
			}
		}
		frappe.call({
            method: "ehc_customization.ehc_customization.doctype.violation_request.api.api.query_filters",
            args: {
                user: frappe.session.user_email
            },
            callback: function(r) {
				if(frappe.session.user != 'Administrator'){
					if (r.message) {
						var reportedEmployees = r.message;
						frm.set_query('employee', function() {
							return {
								filters: [
									['Employee', 'name', 'in', reportedEmployees]
								]
							};
						});
					}
				}
            }
        });

	},
	employee(frm){
		frappe.call({
			method: 'ehc_customization.ehc_customization.customizations.attendance_request.permission.permission_query.manager_self',
			args: {
				employee: frm.doc.employee
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('user', r.message);
				}
			}
		});
		get_late_entries(frm)
	},
	month(frm){
		if(frm.doc.employee){
			get_late_entries(frm)
		}
	},
	validate(frm){
		frappe.db.get_value('Employee', frm.doc.employee, 'user_id')
		.then(ret => {	
			if(ret.message.user_id == frappe.session.user){
				frm.set_value('status', 'Forward To Manager')
				var paragraphContent = $('.ql-editor.read-mode')[0].innerText.trim();
				if (!paragraphContent) {
					frappe.msgprint(__('Please fill in the Employee Reason field.'));
					frappe.validated = false;
				}
			}
			if(frm.doc.status == 'Forward To Employee' && frm.doc.email_id){
				frappe.call({
					method: 'ehc_customization.ehc_customization.doctype.violation_request.api.api.update_permission',
					args: {
						email: frm.doc.email_id,
						employee: frm.doc.employee
					},
					callback: function(response) {			
						// frm.set_value('late_count', response.message)			
						
					},
				});

			}
		})
		
	},
	status(frm){
		if(frm.doc.status == 'Forward To HR'){
			frappe.db.get_value('Employee', frm.doc.employee, 'custom_hr_team')			
			.then(ret => {
				if(ret.message.custom_hr_team){
					frm.set_value('hr_details', ret.message.custom_hr_team)
				}else{
					frm.set_value('hr_details', '')
					frappe.msgprint(__('HR Details not assigned for Employee'));
				}
			})
		}
		if(frm.doc.status == 'Forward To Attendance Team'){
			frappe.db.get_value('Employee', frm.doc.employee, 'custom_attendance_team')			
			.then(ret => {
				if(ret.message.custom_attendance_team){
					frm.set_value('attendance_team', ret.message.custom_attendance_team)
				}else{
					frm.set_value('attendance_team', '')
					frappe.msgprint(__('Attendance Team Details not assigned for Employee'));

				}
			})
		}
	},
	refresh: function(frm) {
        if (frm.doc.status == 'Forward To HR' || frm.doc.status == 'Forward To Attendance Team') {
			if(frappe.session.user == frm.doc.hr_details || frappe.session.user == frm.doc.attendance_team || frappe.session.user=='Administrator')
            frm.add_custom_button(__('Attendance Deduction'), function() {
                makededuction(frm);
            });
         }
    }
});

function makededuction(frm) {
    frappe.model.open_mapped_doc({
        method: "ehc_customization.ehc_customization.doctype.violation_request.api.api.deduction_mapping",
        frm: frm
    });
}

function get_late_entries(frm){
	frappe.call({
		method: 'ehc_customization.ehc_customization.doctype.violation_request.api.api.get_late_details',
		args: {
			employee: frm.doc.employee,
			month: frm.doc.month
		},
		callback: function(response) {			
			frm.set_value('late_count', response.message)			
			
		},
	});
}