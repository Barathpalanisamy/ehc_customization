
frappe.provide("ehc_customization.pages");
frappe.pages['EHC Organizational Chart'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("EHC Organizational Chart"),
		single_column: true,
	});

	$(wrapper).bind("show", () => {
		frappe.require("ehc_hierarchy_chart.bundle.js", () => {
			let organizational_chart;
			let method = "hrms.hr.page.organizational_chart.organizational_chart.get_children";

			if (frappe.is_mobile()) {
				organizational_chart = new ehc_customization.HierarchyChart("Employee", wrapper, method);
			} else {
				organizational_chart = new ehc_customization.HierarchyChart("Employee", wrapper, method);
			}

			frappe.breadcrumbs.add("Ehc Customization");
			organizational_chart.show();
		});
	});
};