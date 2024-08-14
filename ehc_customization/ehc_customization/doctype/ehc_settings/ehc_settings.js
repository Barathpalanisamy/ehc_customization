// Copyright (c) 2024, 8848digital and contributors
// For license information, please see license.txt

frappe.ui.form.on('EHC Settings', {
	onload_post_render: function(frm) {
		frm.set_query('editable_budget', function() {
            return {
                filters: {
                    docstatus: '1'
                }
            };
        });
	}
});
