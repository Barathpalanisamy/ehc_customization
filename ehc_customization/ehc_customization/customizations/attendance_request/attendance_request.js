frappe.ui.form.on('Attendance Request', {
    refresh: function(frm) {
        var currentDate = frappe.datetime.now_date();
        var maxDate = frm.doc.from_date;
        if (currentDate > maxDate) {
            frm.set_df_property('end_time', 'read_only', 1);
            frm.disable_save();
            frm.set_read_only();
        }
    },
    onload: function(frm) {
        var currentDate = frappe.datetime.now_date();
        var maxDate = frm.doc.from_date;
        if (currentDate > maxDate) {
            frm.set_df_property('end_time', 'read_only', 1);
            frm.disable_save();
            frm.set_read_only();
        }
        if(frm.doc.employee && frm.doc.__islocal){
            frm.trigger('employee')
        }
        frappe.call({
            method: "ehc_customization.ehc_customization.doctype.violation_request.api.api.query_filter",
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
						});					}
				}
            }
        });
    },
    custom_reason(frm){
        frappe.call({
            method: 'ehc_customization.ehc_customization.customizations.attendance_request.override.override.update_available_hours',
            args: {
                doc: frm.doc
            },
            callback: function (response) {
                if (response.message) {
                    frm.set_value("custom_available_hours", response.message);
                }
            }
        });
    },
    employee(frm){
        if(frm.doc.employee && frm.doc.employee != '__employee_name'){
            frappe.call({
                method: 'ehc_customization.ehc_customization.customizations.attendance_request.permission.permission_query.manager_self',
                args: {
                    employee: frm.doc.employee
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('custom_reporting_manager', r.message);
                    } else {
                        frappe.throw(__('User Not Linked With Manager or Reporting Manager Not Assigned for this Employee'));
                    }
                }
            });
        }
    }
});