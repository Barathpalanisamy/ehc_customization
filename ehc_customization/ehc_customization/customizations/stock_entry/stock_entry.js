frappe.ui.form.on('Stock Entry', {
    onload_post_render: function (frm) {
        frm.fields_dict['items'].grid.get_field('accounting_department').get_query = function (doc, cdt, cdn) {
            var child = locals[cdt][cdn];

            if (child.cost_center) {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        'cost_center': child.cost_center,
                    }
                }
            };
        }
        if (frm.doc.custom_cost_center) {
            frm.set_query('accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.custom_cost_center
                    }
                };
            });
        }
    },
    onload: function (frm) {
        frm.set_query('custom_cost_center', () => {
            return {
                filters: {
                    'is_group': 0
                }
            };
        });
        frm.set_query('accounting_department', () => {
            return {
                filters: {
                    'is_group': 0
                }
            };
        });

    },
    custom_cost_center: function (frm) {
        var cost_center = frm.doc.custom_cost_center;
        frm.set_value('accounting_department', '');
        if (cost_center) {
            frm.set_query('accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: cost_center
                    }
                };
            });
        }
        else {
            frm.set_query('accounting_department', () => {
                return {
                    filters: {
                        'is_group': 0
                    }
                };
            });
        }
        update_items(frm, "custom_cost_center");
    },
    accounting_department: function (frm) {
        update_items(frm, "accounting_department");
    }
});

function update_items(frm, field) {
    frappe.db.get_single_value('EHC Settings', 'update_child').then(value => {
        if (value) {
            $.each(frm.doc.items, function (index, item) {
                frappe.model.set_value(item.doctype, item.name, field, frm.doc[field]);
            });
            refresh_field("items");
        }
    })
}