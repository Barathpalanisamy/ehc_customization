frappe.ui.form.on('Job Profile Mapping', {
    setup: function (frm) {
        frm.set_query("source_web_form", () => {
            return {
                filters: {
                    doc_type: frm.doc.source,
                },
            };
        });
        frm.set_query("target_web_form", () => {
            return {
                filters: {
                    doc_type: frm.doc.target,
                },
            };
        });
    },
    refresh: function(frm) {
        frm.add_custom_button(__("Get Fields"), () => {
            frappe.call({
                method: 'ehc_customization.ehc_customization.doctype.job_profile_mapping.api.api.get_fields',
                args: {
                    source: frm.doc.source,
                    target: frm.doc.target
                },
                callback: function (response) {
                    if (response.message) {
                        var fields = response.message;
                        if(frm.doc.source_web_form && frm.doc.target_web_form){
                            fields.forEach(function (field) {
                                frm.add_child("mapping_fields", {
                                    source_fields: field['source_label'],
                                    target_fields: field['target_label'],
                                    source_fieldname: field['source_fieldname'],
                                    target_fieldname: field['target_fieldname'],
                                });
                                frm.refresh_field("mapping_fields");
                            });
                        }else{
                            frappe.throw(__("Please Select Source Web Form and Target Web form"));
                        }
                    }
                }
            });
        });
        frm.trigger("enabled");
        frm.trigger("set_source_fields");
        frm.trigger("set_target_fields");
    },
    enabled: function (frm) {
        var doc = frm.doc;
        if (!frm.is_new()) {
            frm.toggle_display(["sb1", "sb3", "modules_access"], doc.enabled);
            frm.set_df_property("enabled", "read_only", 0);
        }

        if (frappe.session.user !== "Administrator") {
            frm.toggle_enable("email", frm.is_new());
        }
    },
    set_source_fields(frm) {
        frappe.call({
            method: 'ehc_customization.ehc_customization.doctype.job_profile_mapping.api.api.get_additional_fields',
            args: {
                doctype: frm.doc.source,
            },
            callback: function (response) {
                if (response.message) {
                    frappe.meta.get_docfield('Mapped Fields', 'source_fields',frm.doc.name).options = (response.message).join('\n');
                }
            }
        });
    },
    set_target_fields(frm) {
        frappe.call({
            method: 'ehc_customization.ehc_customization.doctype.job_profile_mapping.api.api.get_additional_fields',
            args: {
                doctype: frm.doc.target,
            },
            callback: function (response) {
                if (response.message) {
                    frappe.meta.get_docfield('Mapped Fields', 'target_fields',frm.doc.name).options = (response.message).join('\n');
                }
            }
        });
    },
});
frappe.ui.form.on("Mapped Fields", {
    source_fields: function (frm, cdt, cdn) {
        frappe.call({
            method: 'ehc_customization.ehc_customization.doctype.job_profile_mapping.api.api.get_fieldname',
            args: {
                doctype: frm.doc.source,
                field_type: frappe.model.get_value(cdt, cdn, 'source_fields')
            },
            callback: function (response) {
                if (response.message) {
                    frappe.model.set_value(cdt, cdn, 'source_fieldname', response.message);
                }
            }
        });
    },
    target_fields: function (frm, cdt, cdn) {
        frappe.call({
            method: 'ehc_customization.ehc_customization.doctype.job_profile_mapping.api.api.get_fieldname',
            args: {
                doctype: frm.doc.target,
                field_type: frappe.model.get_value(cdt, cdn, 'target_fields')
            },
            callback: function (response) {
                if (response.message) {
                    frappe.model.set_value(cdt, cdn, 'target_fieldname', response.message);
                }
            }
        });
    },
});