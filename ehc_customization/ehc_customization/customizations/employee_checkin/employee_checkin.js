frappe.ui.form.on("Employee Checkin", {
    onload: function (frm) {
        frappe.call({
            method: "ehc_customization.ehc_customization.doctype.violation_request.api.api.query_filter",
            args: {
                user: frappe.session.user_email
            },
            callback: function(r) {
                if(frappe.session.user != 'Administrator'){
                    if (r.message) {
                        var reportedEmployees = r.message;
                        console.log(reportedEmployees)
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
        frappe.call({
            method: "ehc_customization.ehc_customization.customizations.employee_checkin.permission.permission_query.check_read_only",
            args: {
                user: frappe.session.user_email
            },
            callback: function(r) {
                if(frappe.session.user != 'Administrator'){
                    if (r.message) {
                        if(r.message == 'Employee'){
                            frm.set_df_property('time', 'read_only', 1)
                        }
                    }
                }
            }
        });
    }
})
