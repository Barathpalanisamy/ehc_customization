frappe.ui.form.on("Pick List", {
	refresh: function (frm) {
		frm.add_custom_button(__("Sort Items as per warehouse"), function () {
			frappe.call({
				method: "ehc_customization.ehc_customization.customizations.pick_list.pick_list.order_items_as_per_warehouse",
				args: {
					doc: frm.doc.name,
				},
				callback: function (r) {
					if (r.message) {
						frm.reload_doc();
					}
				},
			});
		});
	},
});
