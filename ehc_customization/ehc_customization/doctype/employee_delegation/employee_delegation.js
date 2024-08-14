// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Delegation', {
	designation: function (frm, cdt, cdn) {
		if (frm.doc.designation) {
			frappe.call({
				method: "ehc_customization.ehc_customization.doctype.employee_delegation.doc_events.utility_functions.designation_details",
				args: {
					designation: frm.doc.designation,
				},
				callback: function (r) {
					frm.doc.employee_transfer_details = [];
					frm.doc.responsibility_details = [];
					r.message.forEach(function (message) {

						var new_row = frm.add_child('employee_transfer_details');
						var new_row1 = frm.add_child('responsibility_details');

						new_row.property = message["property"];
						new_row.type = message["type"];
						new_row1.property = message["property"];
						new_row1.type = message["type"];

					});
					refresh_field("employee_transfer_details");
					refresh_field("responsibility_details");
				},

			});
		}
		else {
			frm.doc.employee_transfer_details = [];
			frm.doc.responsibility_details = [];
			refresh_field("employee_transfer_details");
			refresh_field("responsibility_details");

		}
	},
	before_submit(frm) {
		var table1 = frm.doc.employee_transfer_details || [];
		var table2 = frm.doc.responsibility_details || [];

		if (table1.length !== table2.length) {
			frappe.confirm(
				__("Do you want to update current responsibilities for the future?"),
				function () {

					frappe.call({
						method: "ehc_customization.ehc_customization.doctype.employee_delegation.doc_events.utility_functions.transfer_details_updation",
						args: {
							doc: frm.doc
						},
						callback: function (r) {
						},
					});

				}
			);
		}
		for (var i = 0; i < table1.length; i++) {
			var row1 = table1[i];
			var row2 = table2[i];

			if (row1.property !== row2.property || row1.type !== row2.type) {
				frappe.confirm(
					__("Do you want to update current responsibilities for the future?"),
					function () {
						frappe.call({
							method: "ehc_customization.ehc_customization.doctype.employee_delegation.doc_events.utility_functions.transfer_details_updation",
							args: {
								doc: frm.doc
							},
							callback: function (r) {
							},
						});

					}
				);
			}
		}

	}


});