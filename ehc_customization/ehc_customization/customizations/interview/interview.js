frappe.ui.form.on("Interview", {
    async  render_feedback(frm){
        let role = await frappe.db.get_single_value("Job Settings","all_feadback")

        frappe.require("interview.bundle.js", () => {
            const wrapper = $(frm.fields_dict.feedback_html.wrapper);
            const feedback_html = frappe.render_template("interview_feedback_new", {
                feedbacks: frm.feedback,
                average_rating: flt(frm.doc.average_rating * 5, 2),
                reviews_per_rating: frm.reviews_per_rating,
                skills_average_rating: frm.skills_average_rating,
                role: role
            });
            $(wrapper).empty();
            $(feedback_html).appendTo(wrapper);
        });
    },
})