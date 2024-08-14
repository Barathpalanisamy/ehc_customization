
frappe.ui.form.on('Designation', {
    employee_responsibility: function (frm) {
        update_table(frm)
    },

});


function update_table(frm, field) {
    if (frm.doc.employee_responsibility) {
        frappe.call({
            method: "ehc_customization.ehc_customization.customizations.designation.designation.designation_details",
            args: {
                responsibility: frm.doc.employee_responsibility,
            },
            callback: function (r) {
                frm.doc.transfer_details = [];
                r.message.forEach(function (message) {

                    var new_row = frm.add_child('transfer_details');

                    new_row.property = message["property"];
                    new_row.type = message["type"];
                });
                refresh_field("transfer_details");
            },

        });
    }
    else {
        frm.doc.transfer_details = []
        refresh_field("transfer_details");

    }
}