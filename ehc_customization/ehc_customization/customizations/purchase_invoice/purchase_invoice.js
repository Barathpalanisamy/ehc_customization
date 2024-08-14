frappe.ui.form.on('Purchase Invoice', {
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
        if (frm.doc.cost_center) {
            frm.set_query('accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.cost_center
                    }
                };
            });
        }
        enable_fields(frm)

    },
    refresh: function(frm) {
        enable_fields(frm)
    },
    validate: function(frm){
        update_table(frm)
    },
    apply_discount_on: function(frm){
        update_table(frm)
    },

    cost_center: function (frm) {
        var cost_center = frm.doc.cost_center;
        frm.set_value('accounting_department', '');
        frm.set_query('accounting_department', () => {
            return {
                query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                filters: {
                    cost_center: cost_center
                }
            };
        });
        update_items(frm, "cost_center");
    },
    accounting_department: function (frm) {
        update_items(frm, "accounting_department");
    }
});
frappe.ui.form.on('Purchase Invoice Item', {
    items_add: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        frappe.db.get_single_value('EHC Settings', 'update_child').then(value => {
            if (value) {
                frappe.model.set_value(cdt, cdn, 'cost_center', frm.doc.cost_center);
                frappe.model.set_value(cdt, cdn, 'accounting_department', frm.doc.accounting_department);

            }
        })
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

frappe.ui.form.on('Purchase Invoice Discounts', {
    // Trigger recalculation whenever a row in the child table is updated
    percentage: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if(frm.doc.apply_discount_on == 'Grand Total'){
            var base_grand_total = frm.doc.base_total + tax(frm) || 0;
        }else{
            var base_grand_total = frm.doc.base_total|| 0;
    
        }
        if (row.percentage !== null) {
            var calculation = (base_grand_total * row.percentage) / 100;
            if (calculation !== row.custom_amount) {
                frappe.model.set_value(cdt, cdn, 'custom_amount', calculation);
            }
        }
        calculateTotalAmount(frm);
    },
    custom_multiple_discount_remove: function (frm, cdt, cdn) {
        calculateTotalAmount(frm);
    },
    custom_amount: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if(frm.doc.apply_discount_on == 'Grand Total'){
            var base_grand_total = frm.doc.base_total + tax(frm) || 0;
        }else{
            var base_grand_total = frm.doc.base_total|| 0;
    
        }
        if (row.custom_amount !== null) {
            var calculation = (row.custom_amount / base_grand_total) * 100;
            if (calculation !== row.percentage) {
                frappe.model.set_value(cdt, cdn, 'percentage', calculation);
            }
        }
    }
});

function calculateTotalAmount(frm) {
    var totalAmount = 0;
    frm.doc.custom_multiple_discount.forEach(function (row) {
        totalAmount += row.percentage;
    });
    frm.set_value('additional_discount_percentage', totalAmount);
}


function tax(frm) {
    var totaltax = 0;
    frm.doc.taxes.forEach(function(row) {
        totaltax += row.base_tax_amount;
    });
    return totaltax
}

function enable_fields(frm) {
    frappe.call({
        method: 'ehc_customization.ehc_customization.utility.accounting_filter.multiple_account',
        callback: function(response) {
            frm.toggle_display('custom_multiple_discount', response.message);
            frm.set_df_property('additional_discount_percentage', 'read_only', response.message);
            frm.set_df_property('discount_amount', 'read_only', response.message);
        }
    });
}

function update_table(frm){
    if(frm.doc.apply_discount_on == 'Grand Total'){
        setTimeout(function() {
            var base_grand_total = frm.doc.base_total + tax(frm) || 0;
            console.log(base_grand_total)
            $.each(frm.doc.custom_multiple_discount, function (index, item) {
                frappe.model.set_value(item.doctype, item.name, 'custom_amount', base_grand_total *(item.percentage)/100);
            });
            calculateTotalAmount(frm)
        }, 1000);
    }else{
        setTimeout(function() {
            var base_grand_total = frm.doc.base_total|| 0;
            $.each(frm.doc.custom_multiple_discount, function (index, item) {
                frappe.model.set_value(item.doctype, item.name, 'custom_amount', base_grand_total *(item.percentage)/100);
            });
            calculateTotalAmount(frm)
        }, 1000);
    }
}

