frappe.ui.form.on('Permission Policy', {
	previous_time_interval: '',
    time_interval(frm) {
        var previous_interval = frm.events.previous_time_interval;

        if (previous_interval === 'Monthly') {
            if (frm.doc.time_interval === 'Daily') {
                $.each(frm.doc.allocation, function (index, item) {
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) / 30);
                });
            } else if (frm.doc.time_interval === 'Annual') {
                $.each(frm.doc.allocation, function (index, item) {
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) * 12);
                });
            }
        } else if (previous_interval === 'Daily') {
            if (frm.doc.time_interval === 'Monthly') {
                $.each(frm.doc.allocation, function (index, item) {
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) * 30);
                });
            } else if (frm.doc.time_interval === 'Annual') {
                $.each(frm.doc.allocation, function (index, item) {
                    var cal = item.allocated_time  * 30
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (cal) * 12);
                });
            }
        } else if (previous_interval === 'Annual') {
            if (frm.doc.time_interval === 'Monthly') {
                $.each(frm.doc.allocation, function (index, item) {
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (item.allocated_time) / 12);
                });
            } else if (frm.doc.time_interval === 'Daily') {
                $.each(frm.doc.allocation, function (index, item) {
                    var cal = item.allocated_time /12
                    frappe.model.set_value(item.doctype, item.name, 'allocated_time', (cal) / 30);
                });
            }
        }
        frm.events.previous_time_interval = frm.doc.time_interval;

        refresh_field("allocation");
    },
    after_save : function(frm) {
        if ( !frm.doc.__islocal) {
        frappe.call({
			method: 'ehc_customization.ehc_customization.utility.policy_assignment.calculate_permission_type',
			args: {
				doc: frm.doc
			},
			callback: function(response) {
				console.log(response)
			}
		})
    }
    },
    refresh(frm){
        frm.events.previous_time_interval = frm.doc.time_interval;
    frm.add_custom_button(__("Add Policy Entry"), function () {
        
            let d = new frappe.ui.Dialog({
                title: "Add Policy Entries",
                fields: [
                    {
                        label: __("Month"),
                        fieldname: "month",
                        fieldtype: "Select",
                        options: [
                            { "label": "January", "value": "January" },
                            { "label": "February", "value": "February" },
                            { "label": "March", "value": "March" },
                            { "label": "April", "value": "April" },
                            { "label": "May", "value": "May" },
                            { "label": "June", "value": "June" },
                            { "label": "July", "value": "July" },
                            { "label": "August", "value": "August" },
                            { "label": "September", "value": "September" },
                            { "label": "October", "value": "October" },
                            { "label": "November", "value": "November" },
                            { "label": "December", "value": "December" }
                        ],
                        reqd: frm.doc.time_interval === 'Annual' ? 0 : 1,
                        hidden: frm.doc.time_interval === 'Annual' ? true : false
                    },
                    {
                        label: __("Time Interval"),
                        fieldname: "time_interval",
                        fieldtype: "Select",
                        options: 'Annual',
                        default: 'Annual',
                        hidden: frm.doc.time_interval === 'Annual' ? false : true

                    },
                    {
                        label: __("Permission Type"),
                        fieldname: "selected_items",
                        fieldtype: "MultiSelect",
                        options: getCheckboxOptions(),
                        reqd:1
                    },
                    {
                        label: __("Allocated Time"),
                        fieldname: "allocated_time",
                        fieldtype: "Float"
                    }
                ],

                primary_action_label: "Submit",
                primary_action(values) {
                    frappe.call({
                        method: "ehc_customization.ehc_customization.utility.policy_assignment.set_entries",
                        args: {
                            value: values,
                        },
                        callback: function (r) {
                            if (r.message) {
                                r.message.forEach(function(data) {
                                    if (frm.doc.allocation) {
                                        var existing_row = frm.doc.allocation.find(row => row.month === data.month && row.permission_type === data.permission_type);
                                        if (existing_row) {
                                            // Update available time if the row exists
                                            existing_row.allocated_time = existing_row.allocated_time + data.allocated_time;
                                            existing_row.available_time = existing_row.available_time + data.available_time;
                                        } else {
                                            var new_row = frm.add_child('allocation');
                                            new_row.month= data.month;
                                            new_row.permission_type = data.permission_type;
                                            new_row.allocated_time = data.allocated_time;
                                            new_row.available_time = data.available_time;
                                        }
                                    }else{
                                        var new_row = frm.add_child('allocation');
                                        new_row.month= data.month;
                                        new_row.permission_type = data.permission_type;
                                        new_row.allocated_time = data.allocated_time;
                                        new_row.available_time = data.available_time;
                                    }
                                })
                                frm.refresh_field('allocation'); 
                            }
                        },
                    });
                   

                    d.hide();
                },
            });
            
            d.show();

        });
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Permission Policy Assignment'), function() {
                makePolicyAssignment(frm);
            }, __('Create'));
        }

    },
    
})

function makePolicyAssignment(frm) {
    frappe.model.open_mapped_doc({
        method: "ehc_customization.ehc_customization.utility.policy_assignment.make_policy_assignment",
        frm: frm
    });
}

function getCheckboxOptions() {
    var options = [];
    frappe.call({
        method: 'ehc_customization.ehc_customization.utility.policy_assignment.get_policy_type',
        async: false,
        callback: function(response) {
            if (response.message) {
                options = response.message;
            }
        }
    });
    return options;
}

frappe.ui.form.on('Permission hours', {
    allocated_time: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn]; 
        frappe.model.set_value(cdt, cdn, 'available_time', item.allocated_time);

    }
});

