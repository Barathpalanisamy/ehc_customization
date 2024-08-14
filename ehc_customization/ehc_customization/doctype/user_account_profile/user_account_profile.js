// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on("User Account Profile", {
	refresh: function (frm) {
		frm.set_query("parent_profile", function () {
			return {
				filters: {
					head: 1,
				},
			};
		});
	},
});
