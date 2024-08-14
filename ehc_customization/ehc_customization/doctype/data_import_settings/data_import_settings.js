frappe.ui.form.on('Data Import Settings', {
	refresh: function (frm) {
		frappe.call({
			method: 'ehc_customization.ehc_customization.customizations.data_import.override.data_import_override.get_additional_salary_fields',
			callback: function (response) {
				if (response.message) {
					var fields = response.message;
					var options = [];
					fields.forEach(function (field) {
						options.push({ 'value': field, 'label': field });
					});
					frm.fields_dict.column_mapping.grid.update_docfield_property('new_column', 'options', options);
				}
			}
		});
	}
});

