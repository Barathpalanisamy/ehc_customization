frappe.listview_settings['Permission Policy Assignment'] = {
	onload: function (list_view) {
		let me = this;
		list_view.page.add_inner_button(__("Bulk Permission Policy Assignment"), function () {
			me.dialog = new frappe.ui.form.MultiSelectDialog({
				doctype: "Employee",
				target: cur_list,
				setters: {
					employee_name: '',
					company: '',
					department: '',
				},
				data_fields: [{
					fieldname: 'permission_policy',
					fieldtype: 'Link',
					options: 'Permission Policy',
					label: __('Permission Policy'),
					reqd: 1
				}
				],
				get_query() {
					return {
						filters: {
							status: ['=', 'Active']
						}
					};
				},
				add_filters_group: 1,
				primary_action_label: "Assign",
				action(employees, data) {
					frappe.call({
						method: 'ehc_customization.ehc_customization.utility.policy_assignment.create_policy_for_multiple_employees',
						async: false,
						args: {
							employees: employees,
							data: data
						}
					});
					cur_dialog.hide();
				}
			});
		});
	},
}