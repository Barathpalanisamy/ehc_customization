frappe.ui.form.on('Budget', {
    refresh: function (frm, cdt, cdn) {
        if (!frm.doc.custom_akd_total_budget) {
            budget_total(frm, cdt, cdn);
        }
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Budget Transfer'), function () {
                frappe.new_doc("Budget Transfer", { "posting_date": frappe.datetime.nowdate() }, doc => {
                    doc.from_budget_against = frm.doc.budget_against;
                    doc.from_budget = frm.doc.name;
                    doc.from_fiscal_year = frm.doc.fiscal_year;
                    doc.custom_cost_center = frm.doc.cost_center;
                    doc.custom_accounting_department = frm.doc.accounting_department;
                });
            }, __('Transfer'));
        }
        frm.trigger('custom_editable_budget')
    },
    validate: function (frm, cdt, cdn) {
        budget_total(frm, cdt, cdn);
        if(!frm.doc.custom_apply_budget_restrictions){
            frm.trigger('action_if_annual_budget_exceeded')
            frm.trigger('action_if_accumulated_monthly_budget_exceeded')
            frm.trigger('applicable_on_material_request')
            frm.trigger('applicable_on_purchase_order')
        }
    },
    onload_post_render: function (frm) {
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
    },
    action_if_annual_budget_exceeded: function(frm){
        console.log('hjk')
        frm.set_value('custom_expense_annual', frm.doc.action_if_annual_budget_exceeded)
    },
    action_if_accumulated_monthly_budget_exceeded: function(frm){
        frm.set_value('custom_expense_monthly', frm.doc.action_if_accumulated_monthly_budget_exceeded)
    },
    applicable_on_material_request: function(frm){
        frm.set_value('custom_mr', frm.doc.applicable_on_material_request)

    },
    applicable_on_purchase_order: function(frm){
        frm.set_value('custom_po', frm.doc.applicable_on_purchase_order)
    },
    custom_apply_budget_restrictions: function(frm){
        if(frm.doc.custom_apply_budget_restrictions == 0 && !frm.doc.__islocal){
            frm.set_value('action_if_annual_budget_exceeded', frm.doc.custom_expense_annual)
            frm.set_value('action_if_accumulated_monthly_budget_exceeded', frm.doc.custom_expense_monthly)
            frm.set_value('applicable_on_material_request', frm.doc.custom_mr)
            frm.set_value('applicable_on_purchase_order', frm.doc.custom_po)

        }
    },
    custom_editable_budget: function(frm){
        frappe.db.get_single_value('EHC Settings', 'editable_budget').then(value => {
            if (value && (value === frm.doc.name) && frm.doc.custom_editable_budget === 1) {
                if (frm.doc.custom_editable_budget == 1){
                    frm.add_custom_button(__('Edit Budget'), function() {				
                        let d = new frappe.ui.Dialog({
                            title: "Edit Budget",
                            fields: [
                                {
                                    label: __("Budget"),
                                    fieldname: "budget",
                                    fieldtype: "Link",
                                    options: 'Budget',
                                    default: frm.doc.name,
                                    read_only: 1,
                                },
                                {
                                    fieldname: 'budget_account_table',
                                    fieldtype: 'Table',
                                    label: 'Budget Accounts',
                                    cannot_add_rows: true,
                                    fields: [
                                        {
                                            fieldtype: 'Link',
                                            fieldname: 'account_name',
                                            label: 'Account Name',
                                            options:'Account',
                                            read_only:1,
                                            in_list_view: 1
                                        },
                                        {
                                            fieldtype: 'Currency',
                                            fieldname: 'account_value',
                                            label: 'Account Value',
                                            in_list_view: 1
                                        }
                                    ],
                                    data: [],
                                    get_data: function() {
                                        return [];
                                    }
                                }
                            ],
                            primary_action_label: 'Update Budget',
                            primary_action(values) {
                                    frappe.call({
                                        method: "ehc_customization.ehc_customization.customizations.budget.api.utility.update_budget_accounts",
                                        args: {
                                            budget: frm.doc.name,
                                            accounts: values.budget_account_table
                                        },
                                        callback: function(response) {
                                            if (response.message === 'success') {
                                                frm.reload_doc()
                                                frappe.msgprint(__('Budget updated successfully.'));
                                            } else {
                                                frappe.msgprint(__('Failed to update budget.'));
                                            }
                                        }
                                    });
                                d.hide();
                            }
                        });
                        if(frm.doc.name) {
                            
                            frappe.call({
                                method: "ehc_customization.ehc_customization.customizations.budget.api.utility.get_budget_accounts",
                                args: {
                                    budget: frm.doc.name
                                },
                                callback: function(response) {
                                    let budget_accounts = response.message;
                                    
                                    let child_table = d.fields_dict.budget_account_table.df.data;
                                    child_table.length = 0;
                                    
                                    budget_accounts.forEach(account => {
                                        child_table.push({
                                            account_name: account.account,
                                            account_value: account.budget_amount
                                        });
                                    });
                                    
                                    d.fields_dict.budget_account_table.grid.refresh();
                                }
                            });
                        } else {
                            d.fields_dict.budget_account_table.df.data = [];
                            d.fields_dict.budget_account_table.grid.refresh();
                        }

                        d.show();
                        
                    });

                }
            }else{
                frm.remove_custom_button('Edit Budget');
            }
        })
    }
})

function budget_total(frm, cdt, cdn) {
    var accounts = frm.doc.accounts;
    var total = 0;
    var total_base_budget = 0;
    for (var i in accounts) {
        frappe.model.set_value(frm.doc.accounts[i].doctype, frm.doc.accounts[i].name, "custom_akd_budget_before_transfer", frm.doc.accounts[i].budget_amount);
        total = total + accounts[i].budget_amount;
        total_base_budget = total_base_budget + accounts[i].custom_akd_budget_before_transfer;
    }
    frm.set_value("custom_akd_total_budget", total);
    frm.set_value("custom_akd_total_base_budget", total_base_budget);
}