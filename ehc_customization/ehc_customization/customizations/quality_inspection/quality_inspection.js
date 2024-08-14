frappe.ui.form.on('Quality Inspection', {
    refresh: function(frm) {
        frm.set_query('custom_ehc_evaluator', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'EHC Evaluator'
                }
            };
        });
        frm.set_query('custom_ehc_validator', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'EHC Validator'
                }
            };
        });
        frm.set_query('custom_ehc_investigator', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'EHC Investigator'
                }
            };
        });
        frm.set_query('custom_ehc_approver', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'EHC Approver'
                }
            };
        });
        frm.set_query('custom_network_representative', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'Network Representative'
                }
            };
        });
        frm.set_query('custom_facility_representative_new', function() {
            return {
                query: 'ehc_customization.ehc_customization.customizations.quality_inspection.doc_events.utility_functions.get_user_role',
                filters: {
                    role: 'Facility Representative'
                }
            };
        });

    }
});
