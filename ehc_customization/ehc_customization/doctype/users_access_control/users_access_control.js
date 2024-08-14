frappe.ui.form.on("Users Access Control", {
	refresh: function (frm) {
		show_roles_list(frm);
		frm.save();
		frm.fields_dict["get_roles"].grid.get_field("role").get_query = function (doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			return {
				query: "ehc_customization.ehc_customization.doctype.users_access_control.api.users_role.user_role_query",
				filters: { user: frappe.session.user },
			};
		};
		
                frm.set_query("role_profile", () => {
                        return {
                           filters: {
                             modified_by: frappe.session.user,
                             },
                        };
                });
		frm.add_custom_button(__("Remove Roles"), function () {
			frappe.call({
				method: "ehc_customization.ehc_customization.doctype.users_access_control.users_access_control.role_query",
				args: {
					user: frappe.session.user,
					name: frm.doc.name,
				},
				callback: function (r) {
					var data = r.message || [];

					let d = new frappe.ui.Dialog({
						title: "View Permitted Role",
						fields: [
							{
								label: "",
								fieldname: "role",
								fieldtype: "Table",
								cannot_add_rows: true,
								in_place_edit: false,
								data: data,
								fields: [
									{
										fieldname: "role",
										columns: 2,
										fieldtype: "Data",
										option: "",
										in_list_view: 1,
										label: "Role",
										read_only: true,
									},
								],
							},
						],

						primary_action_label: "Submit",
						primary_action(values) {
							var roleList =
								values && values.role && Array.isArray(values.role)
									? values.role.map((role) => role.role)
									: [];

							frappe.call({
								method: "ehc_customization.ehc_customization.doctype.users_access_control.users_access_control.update_roles",
								args: {
									roles_list: roleList,
									user: frappe.session.user,
									uac: frm.doc.name,
								},
								callback: function (r) {
									if (r.message) {
										frm.reload_doc();
									}
								},
							});

							d.hide();
						},
					});

					d.show();
				},
			});
		});
	},

	role_profile: function (frm) {
		frappe.call({
			method: "ehc_customization.ehc_customization.doctype.users_access_control.users_access_control.get_role_from_role_profile",
			args: {
				role_profile: frm.doc.role_profile,
			},
			callback: function (r) {
				frm.doc.get_roles = [];
				for (let i = 0; i < r.message.length; i++) {
					let d = frm.add_child("get_roles");
					d.role = r.message[i]["role"];
					d.user = frappe.session.user;
				}
				frm.refresh_field("get_roles");
			},
		});
	},
});

frappe.ui.form.on("Get Roles", {
	role(frm, cdt, cdn) {
		let d = locals[cdt][cdn];
		frappe.model.set_value(d.doctype, d.name, "user", frappe.session.user);
	},
});

function show_roles_list(frm) {
	var roles_list = [];
	$.each(frm.doc.roles_assigned || [], function (i, d) {
		if (d.user === frappe.session.user) {
			roles_list.push({
				role: d.role,
				user: d.user,
			});
		}
	});
	if (roles_list.length > 0) {
		set_html_data(frm, roles_list);
	}
}

function set_html_data(frm, roles) {
	var template = `
    <div>
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th class="text-left" width="30%">Role</th>

                </tr>
            </thead>
            <tbody>
                {% for (var i=0; i < roles_list.length; i++) { %}
                    <tr>
                        <td>{{ roles_list[i].role }}</td>
                    </tr>
                {% } %}
            </tbody>
        </table>
    </div>`;
	var html = frappe.render_template(template, { roles_list: roles });
	frm.get_field("users_roles").$wrapper.html(html);
}
