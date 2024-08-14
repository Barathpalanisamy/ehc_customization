frappe.ui.form.on("User", {
	role_profile_name: function (frm) {
		if (frm.doc.role_profile_name == "Job Seeker") {
            frm.doc.user_type = "Website User";
            frm.refresh_field("user_type");
		}
	},
    validate: function(frm){
        if (frm.doc.role_profile_name == "Job Seeker" && frm.doc.user_type == "Website User") {
            frappe.call({
                method: "ehc_customization.customizations.user.user.validate_website_users",
                args: {
                    self: frm,
                },
                callback: function (res) {
                    // console.log(res);
                },
            });
        }
    }
});