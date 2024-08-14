frappe.ui.form.on("Material Request", {
	get_avail_qty: function (frm, item) {
		if (frm.doc.material_request_type == "Material Transfer") {
			if (item && !item.item_code) {
				return;
			}
			let warehouse = "";
			if (item.from_warehouse) {
				warehouse = item.from_warehouse;
			}

			frappe.call({
				method: "ehc_customization.ehc_customization.customizations.material_request.material_request.get_available_qty",
				args: {
					item_code: item.item_code,
					warehouse: warehouse,
					company: frm.doc.company,
				},
				callback: function (r) {
					const d = item;
					const allow_to_change_fields = ["custom_available_qty"];

					if (r.message) {
						$.each(r.message, function (key, value) {
							if (!d[key] || allow_to_change_fields.includes(key)) {
								d[key] = value;
							}
						});

						refresh_field("items");
					}
				},
			});
		}
	},
	onload_post_render: function(frm) {
        frm.fields_dict['items'].grid.get_field('accounting_department').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            if (child.cost_center){
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        'cost_center': child.cost_center
                    }
                }
            };
        }
    },
});

frappe.ui.form.on("Material Request Item", {
	qty: function (frm, doctype, name) {
		const item = locals[doctype][name];
		frm.events.get_avail_qty(frm, item);
	},

	from_warehouse: function (frm, doctype, name) {
		const item = locals[doctype][name];
		frm.events.get_avail_qty(frm, item);
	},

	warehouse: function (frm, doctype, name) {
		const item = locals[doctype][name];
		frm.events.get_avail_qty(frm, item);
	},

	item_code: function (frm, doctype, name) {
		const item = locals[doctype][name];
		frm.events.get_avail_qty(frm, item);
	},
});
