// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permission Allocation', {
	permission_type: function(frm) {
		console.log(frm.doc.permission_type)
		frappe.call({
			method: 'ehc_customization.ehc_customization.utility.policy_assignment.calculate_permission_type',
			args: {
				doc: frm.doc
			},
			callback: function(response) {
				console.log(response)
				if (response.message && response.message.length > 0) {
					for (let i = 0; i < response.message.length; i++) {
						var time = response.message[i].available_time;
						frappe.model.set_value('Type Calculation', frm.doc.time_allocation[i].name, 'available_time', time);
					}
				} else {
					// frm.doc.time_allocation = [];
					refresh_field('time_allocation');
				}
			}
		})

	}
});
