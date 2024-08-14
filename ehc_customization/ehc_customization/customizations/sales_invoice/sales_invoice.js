frappe.ui.form.on('Sales Invoice', {
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
        if (frm.doc.__islocal) {
            frm.set_value('custom_total_amount', 0);
            frm.set_value('custom_payment_mode', 0);
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
    validate(frm) {
        if (frm.doc.ehc1_revenue_type === "Investment") {
            frm.doc.ehc_payment_method = "";
            frm.doc.ehc_trainee_nationality = "";

        }

        if (frm.doc.ehc1_revenue_type === "Course") {
            frm.doc.ehc_payment_method = "";

        }

        if (frm.doc.ehc1_revenue_type === "Patient") {
            frm.doc.ehc_trainee_nationality = "";
        }
    },
    ehc_facility_type: (frm) => {
        if (frm.doc.ehc1_revenue_type === "Patient") {
            if (frm.doc.ehc_payment_method === "Insurance Patient") {
                update_price_list(frm, frm.doc.ehc_facility_type)
            }
        }
    },
    accounting_department: function (frm) {
        update_items(frm, "accounting_department");
    },
    ehc_payment_method: (frm) => {
        if (frm.doc.ehc_payment_method === "Cash Patient") {
            update_price_list(frm, "Cash Patient")
            frappe.db.get_list("Item Group", {
                filters: { 'parent_item_group': 'Cash Items' },
                pluck: 'name'
            }).then((res) => {
                res.push('Cash Items');
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: {
                            "item_group": ['in', res]
                        }
                    };
                });
            });

        }
        else if (frm.doc.ehc_payment_method === "Insurance Patient") {
            if (frm.doc.ehc_facility_type) {
                update_price_list(frm, frm.doc.ehc_facility_type)
            }
            frappe.db.get_list("Item Group", {
                filters: { 'parent_item_group': 'CHI Prices' },
                pluck: 'name'
            }).then((res) => {
                res.push('CHI Prices');
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: {
                            "item_group": ['in', res]
                        }
                    };
                });
            });
        }
        else {
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                return {
                    filters: {
                        "item_group": ['in', frm.doc.ehc_payment_method]
                    }
                };
            });

        }

        if (frm.doc.__islocal) {

            if (frm.doc.__is_ehc_payment_method === undefined) {
                frm.doc.__is_ehc_payment_method = false;
            }
            if (frm.doc.__is_ehc_payment_method) {
                clear_table(frm)

            } else {
                frm.doc.__is_ehc_payment_method = true;
            }
        }
        else {
            clear_table(frm)
        }
    },
    ehc_invoice_type: function (frm) {
        if (frm.doc.ehc1_revenue_type === "Course" || frm.doc.ehc1_revenue_type === "Investment") {
            update_price_list(frm, frm.doc.ehc1_revenue_type)
        }
        if (frm.doc.ehc1_revenue_type === "Patient") {
            if (frm.doc.ehc_payment_method === "Cash Patient") {
                frappe.db.get_list("Item Group", {
                    filters: { 'parent_item_group': 'Cash Items' },
                    pluck: 'name'
                }).then((res) => {
                    res.push('Cash Items');
                    frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                        return {
                            filters: {
                                "item_group": ['in', res]
                            }
                        };
                    });
                });

            } else if (frm.doc.ehc_payment_method === "Insurance Patient") {
                if (frm.doc.ehc_facility_type) {
                    frappe.db.get_list("Item Group", {
                        filters: { 'parent_item_group': 'CHI Prices' },
                        pluck: 'name'
                    }).then((res) => {
                        res.push('CHI Prices');
                        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                            return {
                                filters: {
                                    "item_group": ['in', res]
                                }
                            };
                        });
                    });
                }
            }
            else {
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: { "item_group": frm.doc.ehc_payment_method }
                    };
                });
            }
        }
        else if (frm.doc.ehc1_revenue_type === "Investment") {
            frappe.db.get_list("Item Group", {
                filters: { 'parent_item_group': frm.doc.ehc1_revenue_type },
                pluck: 'name'
            }).then((res) => {
                res.push(frm.doc.ehc1_revenue_type);
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: {
                            "item_group": ['in', res]
                        }
                    };
                });
            });
        }
        else if (frm.doc.ehc1_revenue_type === "Course") {
            var item_group = frm.doc.ehc_trainee_nationality;
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                return {
                    filters: { "item_group": item_group }
                };
            });
        }
        if (frm.doc.__islocal) {

            if (frm.doc.__is_ehc_invoice_type === undefined) {
                frm.doc.__is_ehc_invoice_type = false;
            }
            if (frm.doc.__is_ehc_invoice_type) {
                clear_table(frm)

            } else {
                frm.doc.__is_ehc_invoice_type = true;
            }
        }
        else {
            clear_table(frm)
        }
    },
    ehc_trainee_nationality: function (frm) {
        if (frm.doc.__islocal) {

            if (frm.doc.__ehc_trainee_nationality === undefined) {
                frm.doc.__ehc_trainee_nationality = false;
            }
            if (frm.doc.__ehc_trainee_nationality) {
                clear_table(frm)

            } else {
                frm.doc.__ehc_trainee_nationality = true;
            }
        }
        else {
            clear_table(frm)
        }
        var item_group = frm.doc.ehc_trainee_nationality;
        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
            return {
                filters: { "item_group": item_group }
            };
        });

    }

});

frappe.ui.form.on('Sales Invoice Item', {
    items_add: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        frappe.db.get_single_value('EHC Settings', 'update_child').then(value => {
            if (value) {
                frappe.model.set_value(cdt, cdn, 'cost_center', frm.doc.cost_center);
                frappe.model.set_value(cdt, cdn, 'accounting_department', frm.doc.accounting_department);

            }
        })
        if (frm.doc.ehc1_revenue_type === "Patient") {
            if (frm.doc.ehc_payment_method === "Cash Patient") {
                frappe.db.get_list("Item Group", {
                    filters: { 'parent_item_group': 'Cash Items' },
                    pluck: 'name'
                }).then((res) => {
                    res.push('Cash Items');
                    frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                        return {
                            filters: {
                                "item_group": ['in', res]
                            }
                        };
                    });
                });

            } else if (frm.doc.ehc_payment_method === "Insurance Patient") {
                if (frm.doc.ehc_facility_type) {
                    frappe.db.get_list("Item Group", {
                        filters: { 'parent_item_group': 'CHI Prices' },
                        pluck: 'name'
                    }).then((res) => {
                        res.push('CHI Prices');
                        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                            return {
                                filters: {
                                    "item_group": ['in', res]
                                }
                            };
                        });
                    });
                }
            }
            else {
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: { "item_group": frm.doc.ehc_payment_method }
                    };
                });
            }
        }
        else if (frm.doc.ehc1_revenue_type === "Investment") {
            frappe.db.get_list("Item Group", {
                filters: { 'parent_item_group': frm.doc.ehc1_revenue_type },
                pluck: 'name'
            }).then((res) => {
                res.push(frm.doc.ehc1_revenue_type);
                frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                    return {
                        filters: {
                            "item_group": ['in', res]
                        }
                    };
                });
            });
        }
        else if (frm.doc.ehc1_revenue_type === "Course") {
            var item_group = frm.doc.ehc_trainee_nationality;
            frm.set_query("item_code", "items", function (doc, cdt, cdn) {
                return {
                    filters: { "item_group": item_group }
                };
            });
        }

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
function clear_table(frm) {
    frappe.db.get_single_value('EHC Settings', 'table_clear').then(value => {
        if (value) {
            if (frm.doc.items && frm.doc.items.length > 0) {
                frappe.msgprint(__("The items have been cleared"));
                frm.set_value('items', []);
                frm.set_value('taxes', [])
            }
        }
    })
}

function update_price_list(frm, name) {
    frappe.call({
        method: 'ehc_customization.ehc_customization.customizations.sales_invoice.doc_events.utility_functions.create_update_price_list',
        args: {
            price_list_name: name
        },
        callback: function (response) {
            if (response.message) {
                frm.set_value("selling_price_list", name);
            }
        }
    });

}


function updateTotalAmount(frm) {
    var totalAmount = 0;
    frm.doc.custom_payment_mode.forEach(function (row) {
        totalAmount += row.amount || 0;
    });
    // var writeOffAmount = frm.doc.base_grand_total - (frm.doc.base_grand_total - totalAmount - frm.doc.total_advance);
    // if (frm.doc.base_grand_total - totalAmount - frm.doc.total_advance < 0) {
    //     writeOffAmount = frm.doc.base_grand_total;
    // }
    frm.set_value({ 'custom_total_amount': totalAmount});
}



frappe.ui.form.on('Payment Mode Invoice', {
    custom_payment_mode_remove: function(frm, cdt, cdn){
        updateTotalAmount(frm);
    },
    custom_percentage: function (frm, cdt, cdn) {
        var percentage = locals[cdt][cdn];
        if (percentage.custom_percentage) {
            var calculation = (frm.doc.base_grand_total * percentage.custom_percentage) / 100;
            frappe.model.set_value(cdt, cdn, 'amount', calculation);
        }
    },
    amount: function (frm, cdt, cdn) {
        var amount_value = locals[cdt][cdn].amount;
        var percentage_value = locals[cdt][cdn].custom_percentage;
        var calculation = (frm.doc.base_grand_total * percentage_value) / 100;
        if (calculation !== amount_value) {
            frappe.model.set_value(cdt, cdn, 'custom_percentage', 0);
        }
        updateTotalAmount(frm);


    }
});
