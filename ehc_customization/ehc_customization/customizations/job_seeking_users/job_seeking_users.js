frappe.ui.form.on("Job Seeking Users", {
	role_profile_name: function (frm) {
		if (frm.doc.role_profile_name) {
			frappe.call({
				method: "frappe.core.doctype.user.user.get_role_profile",
				args: {
					role_profile: frm.doc.role_profile_name,
				},
				callback: function (data) {
					frm.set_value("roles", []);
					$.each(data.message || [], function (i, v) {
						var d = frm.add_child("roles");
						d.role = v.role;
					});
				},
			});
		}
	},
	// validate: function (frm) {
	//     if (frm.doc.role_profile_name) {
	// 		frappe.call({
	// 			method: "ehc_customization.ehc_customization.customizations.job_seeking_users.job_seeking_users.assign_roles",
	// 			args: {
	// 				user: frm.doc.name,
	// 				profile: frm.doc.role_profile_name
	// 			},
	// 			callback: function (res) {
	// 				frm.doc.user_type = "System User"
	// 			},
	// 		});
	// 	}
	// 	else{
	// 		frappe.throw(__('Plsease select a Role Profile'))
	// 	}
	// },
	custom_nat_id: function (frm) {
		frappe.call({
			method: "ehc_customization.ehc_customization.customizations.job_seeking_users.api.utility_functions.get_nat_id",
			args: {
				nat_id: frm.doc.custom_nat_id
			},
			callback: function (res) {
				if (res.message == 0) {
					frappe.throw(__('{0} National ID already used', [frm.doc.custom_nat_id]))
				}
			},
		});
	},
});

frappe.ui.form.on("Work Experience", {
	from_date: function (frm) {
		console.log('sssssssssssss')

		updateExperienceYears(frm);

	},
	to_date: function (frm) {
		updateExperienceYears(frm);

	},
	current: function (frm) {
		updateExperienceYears(frm);

	}
})

function differenceInYears(date1, date2) {
	var differenceMs = Math.abs(date2.getTime() - date1.getTime());
	var differenceYears = differenceMs / (1000 * 60 * 60 * 24 * 365);
	differenceYears = parseFloat(differenceYears.toFixed(1));
	return differenceYears
}

function updateExperienceYears(frm) {
	var totalYearsNoOverlap = 0;
	var totalYearsWithOverlap = 0;

	for (var i = 0; i < frm.doc.work_experience.length; i++) {
		var row = frm.doc.work_experience[i];
		var startDate = new Date(row.from_date);
		var endDate = new Date(row.to_date);
		if (row.current == 1) {
			endDate = new Date();
		}

		if (startDate < endDate) {
			var difference = differenceInYears(startDate, endDate);
			totalYearsNoOverlap += difference;

			var overlapDetected = false;

			for (var j = 0; j < i; j++) {
				var prevRow = frm.doc.work_experience[j];
				var prevStartDate = new Date(prevRow.from_date);
				var prevEndDate = new Date(prevRow.to_date);
				if (startDate < prevEndDate && endDate > prevStartDate) {

					if (!overlapDetected) {
						overlapDetected = true;
						var overlapStartDate = startDate < prevStartDate ? prevStartDate : startDate;
						var overlapEndDate = endDate < prevEndDate ? endDate : prevEndDate;
						var overlapDifference = differenceInYears(overlapStartDate, overlapEndDate);
						totalYearsWithOverlap += overlapDifference;
					} else {

						frappe.msgprint(__("Date overlap detected more than once"));

					}
				}
			}
		} else {
			frappe.msgprint(__("End date should be greater than start date"));
		}

	}

	frm.set_value('overlap_experience_in_years', totalYearsWithOverlap)

	var totalexp = totalYearsNoOverlap - totalYearsWithOverlap
	totalexp = parseFloat(totalexp.toFixed(1))

	frm.set_value('experience_years', totalexp);
}
