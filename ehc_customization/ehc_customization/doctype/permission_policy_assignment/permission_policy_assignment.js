// // Copyright (c) 2024, 8848digital and contributors
// // For license information, please see license.txt

frappe.ui.form.on('Permission Policy Assignment', {	
	time_interval(frm) {
        if (frm.doc.time_interval === 'Monthly') {
            $.each(frm.doc.monthly_allocation, function (index, item) { 
                frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) * 30);  
              
            });
        } else {
            $.each(frm.doc.monthly_allocation, function (index, item) {
                if (frm.doc.time_interval === 'Daily') {
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) / 30);

                }
            });
        }
        refresh_field("allocation");
    },

	custom_permission_policy(frm){
        frappe.db.get_value('Permission Policy', frm.doc.custom_permission_policy, 'fiscal_year')
		.then(ret => {
			if(ret.message.fiscal_year){
					
				frm.set_value('fiscal_year', ret.message.fiscal_year)
				
			}
		})
		time_allocation(frm)

	},
    onload_post_render(frm){
        if(frm.doc.custom_permission_policy && !frm.doc.__islocal && frm.doc.docstatus == 0){
            time_allocation(frm)
            frm.add_custom_button(__('Attendance Request'), function() {
                makeattendancerequest(frm);
            }, __('Attendance Request'));

            setTimeout(function() {
                frm.save()
             }, 1000);
            
        }
    },
    employee(frm){
        if(frm.doc.custom_permission_policy){
            time_allocation(frm)
        }
    },
    after_save(frm){
        setTimeout(function() {
            frm.add_custom_button(__('Attendance Request'), function() {
                makeattendancerequest(frm);
            }, __('Attendance Request'));
        }, 500);

    }
});

function makeattendancerequest(frm) {
    frappe.model.open_mapped_doc({
        method: "ehc_customization.ehc_customization.utility.policy_assignment.make_attendance_request",
        frm: frm
    });
}

function time_allocation(frm){
	frappe.call({
		method: 'ehc_customization.ehc_customization.utility.policy_assignment.calculate_monthly_time',
		args: {
			doc: frm.doc
		},
		callback: function(response) {
			frm.clear_table("monthly_allocation"); 
            response.message.forEach(function(data) {
				var new_row = frm.add_child("monthly_allocation");                
				new_row.month = data.month;
				new_row.permission_type = data.permission_type
				new_row.allocated_time = data.allocated_time;
				new_row.available_time = data.available_time
            });
            
            frm.refresh_field("monthly_allocation"); 
            
		},
	});
}