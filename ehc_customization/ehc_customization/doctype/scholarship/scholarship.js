// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on('Scholarship', {
	onload_post_render: function(frm) {
		frm.set_query("scholarship_id", function() {
			return {
				filters: [["processing", "=", 'Start'],['is_end',"=",0],['employee','=', frm.doc.employee],['docstatus','=', 1]]
			};
		});
		if (frm.doc.__islocal){
			frm.set_value('previous_end_date','')
		}
		update_end_button(frm)
		
	},
	refresh(frm){
		update_end_button(frm)
	},
	validate(frm){
		if(frm.doc.docstatus != 1){
			frappe.call({
				method: "ehc_customization.ehc_customization.doctype.scholarship.doc_events.utility_function.get_scholarship_id",
				args: {
					employee: frm.doc.employee
				},
				callback: function(response) {
					if(response && response.message){
						console.log(response.message)
						var scholarship_id = response.message[0];
						var linked_id = response.message[1];
						if (scholarship_id) {
							frm.set_value('scholarship_id', scholarship_id.name)
						} else {
							frappe.msgprint(__("Scholarship ID not found for this employee."));
						}
						if (linked_id) {
							frm.set_value('previous_time_period', linked_id.name)
						}

					}
				}
			});
		}
	}
});

function update_end_button(frm){
	frappe.db.get_single_value('HR Settings', 'custom_scholarship_access_role').then(value => {
		if (value) {
			var role = frappe.user.has_role(value)
			if(role && frm.doc.processing != 'End' && frm.doc.docstatus==1){
				frappe.call({
					method: "ehc_customization.ehc_customization.doctype.scholarship.doc_events.utility_function.get_button",
					args: {
						name: frm.doc.name
					},
					callback: function(response) {
						if(!response.message){
							frm.add_custom_button(__('Update End Status'), function() {
					
								let d = new frappe.ui.Dialog({
									title: "Select End Date",
									fields: [
										{
											label: __("End Date"),
											fieldname: "end_date",
											fieldtype: "Date"
										}
									],
							
									primary_action_label: "Submit",
									primary_action(values) {
										frappe.call({
											method: "ehc_customization.ehc_customization.doctype.scholarship.doc_events.utility_function.end_scholarship",
											args: {
												value: values,
												doc: frm.doc
											},
											callback: function (r) {
												frm.reload_doc();
													
											},
										});
									   
							
										d.hide();
									},
								});
								
								d.show();
								
							});
						}
					}
				});
			}

		
		}
	})
}
