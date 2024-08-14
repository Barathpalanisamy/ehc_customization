frappe.ui.form.on('Payment Entry', {
    onload_post_render: function (frm) {
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
    }
})