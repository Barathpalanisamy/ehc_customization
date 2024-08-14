frappe.query_reports["EHC Initiative Level"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "is_initiative",
			label: __("Is Initiative"),
			fieldtype: "Check",
			default: 1
		},
		{
			fieldname: "top_task",
			label: __("Top Level Task"),
			fieldtype: "Check",
			default: 1,

		},
		{
			fieldname: "parent_task",
			label: __("Parent Task"),
			fieldtype: "Link",
			options: "Task",
			depends_on: "eval:!doc.top_task",
			get_query: function () {
				return {
					filters: [
						["Task", "is_group", "=", 1]
					]
				};
			}
		},
	]
};
