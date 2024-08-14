frappe.ui.form.on('Skill Assessment', {
    rating: function (frm, cdt, cdn) {
        var rating = frappe.model.get_value(cdt, cdn, 'rating');
        var unit = rating
        var calc_rating = unit*5;
        frappe.model.set_value(cdt, cdn, 'custom_rating_no', calc_rating);
        frm.refresh_field('custom_rating_no');

        var d = locals[cdt][cdn];
        var total = 0;
        frm.doc.skill_assessment.forEach(function(d) { total += d.custom_rating_no; });
        frm.set_value('average_rating_number', total);
        frm.refresh_field('average_rating_number');
    },
    skill_assessment_remove: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total = 0;
        frm.doc.skill_assessment.forEach(function(d) { total += d.custom_rating_no; });
        frm.set_value('average_rating_number', total);
        frm.refresh_field('average_rating_number');
    }
});

frappe.ui.form.on('Interview Feeedback', {
    validate: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total = 0;
        frm.doc.skill_assessment.forEach(function(d) { total += d.custom_rating_no; });
        frm.set_value('average_rating_number', total);
        frm.refresh_field('average_rating_number');
    },
})