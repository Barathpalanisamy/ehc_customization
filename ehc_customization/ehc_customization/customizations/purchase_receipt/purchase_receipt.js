frappe.ui.form.on('Purchase Receipt', {
    onload_post_render: function (frm) {
        frm.fields_dict['items'].grid.get_field('accounting_department').get_query = function (doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            if (child.cost_center) {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        'cost_center': child.cost_center
                    }
                }
            };
        }
        if (frm.doc.cost_center){
            frm.set_query('accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.cost_center
                    }
                };
            });
        }
    },
    cost_center: function (frm) {
        var cost_center = frm.doc.cost_center;
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
        update_items(frm, "cost_center");
    },
    accounting_department: function (frm) {
        update_items(frm, "accounting_department");
    }
})

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