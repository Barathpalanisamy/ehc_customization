frappe.ui.form.on('Budget Transfer', {
    refresh: function (frm, cdt, cdn) {
        if (frm.doc.from_budget) {
            frm.trigger("filter_from_account");
        }
        if (frm.doc.to_budget) {
            frm.trigger("filter_to_account");
        }
        frm.trigger("filter_to_budget");
        frm.trigger("filter_from_budget");
    },
    from_budget: function (frm, cdt, cdn) {
        frm.trigger("filter_from_account");
        frm.set_value('from_account', undefined);
    },
    to_budget: function (frm, cdt, cdn) {
        frm.trigger("filter_to_account");
        frm.set_value('to_account', undefined);
    },
    from_budget_against: function (frm, cdt, cdn) {
        frm.trigger("filter_from_budget");
        frm.set_value('from_budget', '');
    },
    to_budget_against: function (frm, cdt, cdn) {
        frm.trigger("filter_to_budget");
        frm.set_value('to_budget', '');
    },
    filter_from_account: function (frm) {
        frm.set_query("from_account", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_from_account",
                filters: {
                    'from_budget': frm.doc.from_budget
                }
            }
        });
    },
    filter_to_account: function (frm) {
        frm.set_query("to_account", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_from_account",
                filters: {
                    'from_budget': frm.doc.to_budget
                }
            }
        });
    },
    to_cost_center: function (frm) {
        if (frm.doc.to_cost_center) {
            frm.set_query('to_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.to_cost_center
                    }
                };
            });
        }
    },
    to_accounting_department:function(frm){
        frm.set_query("to_budget", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_to_budget",
                filters: {
                    'to_budget_against': frm.doc.to_budget_against,
                    'cost_center': frm.doc.to_cost_center,
                    'accounting_department': frm.doc.to_accounting_department,
                    'docstatus': 1
                }
            }
        });
        
    },
    filter_to_budget: function (frm) {
        if (frm.doc.to_accounting_department0){
        frm.set_query("to_budget", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_to_budget",
                filters: {
                    'to_budget_against': frm.doc.to_budget_against,
                    'cost_center': frm.doc.to_cost_center,
                    'accounting_department': frm.doc.to_accounting_department,
                    'docstatus': 1
                }
            }
        });
    }
    else{
        frm.set_query("to_budget", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_to_budget",
                filters: {
                    'to_budget_against': frm.doc.to_budget_against,
                    'cost_center': frm.doc.to_cost_center,
                    'accounting_department': '',
                    'docstatus': 1
                }
            }
        });
    }
    },
    filter_from_budget: function (frm) {
        frm.set_query("from_budget", function () {
            return {
                query: "ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.filter_to_budget",
                filters: {
                    'to_budget_against': frm.doc.from_budget_against,
                    'cost_center': frm.doc.custom_cost_center,
                    'accounting_department': frm.doc.custom_accounting_department,
                    'docstatus': 1
                }
            }
        });
    },


    from_account: function (frm) {
        if (frm.doc.from_account) {
            frappe.call({
                method: 'ehc_customization.ehc_customization.customizations.budget_transfer.doc_events.utility_functions.fetch_budget_before_transfer',
                args: {
                    account: frm.doc.from_account,
                    parent: frm.doc.from_budget,
                    from_budget_against: frm.doc.from_budget_against
                },
                callback: (r) => {
                    frm.set_value('from_budget_before_transfer', r.message.akd_budget_before_transfer);
                    frm.set_value('from_budget_after_transfer', r.message.budget_amount);
                    frm.set_value('from_budget_available', r.message.budget_amount - r.message.budget_available);
                }
            })
        }
        else {
            frm.set_value('from_budget_before_transfer', undefined);
            frm.set_value('from_budget_after_transfer', undefined);
            frm.set_value('from_budget_available', undefined);
        }
    },

    validate: function(frm){
        if(frm.doc.transfer > frm.doc.from_budget_available){
            frappe.throw(__("Budget Transfer Amount can't be greater than Budget Available"));
            frappe.validated = false;
        }
        if(frm.doc.transfer < 0){
            frappe.throw(__("Negative Budget Transfer Amount not Allowed"));
            frappe.validated = false;
        }

        if((frm.doc.from_account && frm.doc.from_budget) === (frm.doc.to_account && frm.doc.to_budget)){
            frappe.throw(__("Transfer Budgets & Accounts are same"));
            frappe.validated = false;
        }
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Account",
                fields: ["name"],
                filters: { "name": frm.doc.to_account, "disabled": 1 },
                limit: 1
            },
            callback: function (response) {
                if (response.message && response.message.length > 0) {
                    frappe.msgprint(__("To Account Not Active"));
                    frappe.validated = false;
                }
            }
        })
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Account",
                fields: ["name"],
                filters: { "name": frm.doc.from_account, "disabled": 1 },
                limit: 1
            },
            callback: function (response) {
                if (response.message && response.message.length > 0) {
                    frappe.msgprint(__("From Account Not Active"));
                    frappe.validated = false;
                }
            }
        })
    },
    onload_post_render: function (frm) {
        if (frm.doc.custom_cost_center) {
            frm.set_query('custom_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.custom_cost_center
                    }
                };
            });
        }
        if (frm.doc.to_cost_center){
            frm.set_query('to_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: frm.doc.to_cost_center
                    }
                };
            });
        }
    },
    custom_cost_center: function (frm) {
        var cost_center = frm.doc.custom_cost_center;
        frm.set_value('custom_accounting_department', '');
        if (cost_center) {
            frm.set_query('custom_accounting_department', () => {
                return {
                    query: 'ehc_customization.ehc_customization.utility.accounting_filter.get_accounting_departments',
                    filters: {
                        cost_center: cost_center
                    }
                };
            });
        }
    },
    to_cost_center: function (frm) {
        var cost_center = frm.doc.to_cost_center;
        frm.set_value('to_accounting_department', '');
        if (cost_center) {
            frm.set_query('to_accounting_department', () => {
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