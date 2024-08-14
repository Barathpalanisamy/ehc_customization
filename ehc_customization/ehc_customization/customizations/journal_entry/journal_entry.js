frappe.ui.form.on('Journal Entry', {
	onload_post_render: function(frm) {
        frm.fields_dict['accounts'].grid.get_field('accounting_department').get_query = function(doc, cdt, cdn) {
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
})

frappe.ui.form.on('Journal Entry Account', {
    cost_center: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'accounting_department', '');
    }
});