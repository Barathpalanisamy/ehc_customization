frappe.ui.form.on('Job Opening', {
    validate:function(frm) {
        if (frm.doc.job_opening_category == "Internal"){
            frm.doc.publish = '0';
            frm.doc.route='';
            frm.refresh_field('route');
        }
        if (frm.doc.job_opening_category == "External"){
            frm.doc.custom_publish_internal = '0';
            frm.doc.route_internal='';
            frm.refresh_field('route_internal');
        }
    },
    job_opening_category:function(frm) {
        if (frm.doc.job_opening_category == "Internal"){
            frm.doc.custom_publish_internal = '0';
            frm.toggle_display("custom_publish_internal",true);
            frm.toggle_display("route_internal",false);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",false);
            frm.refresh_field('internal_job_route');
            frm.doc.publish = '0';
            frm.toggle_display("publish",false);
            frm.refresh_field('publish');
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
            
            // var scrubbedCompany = frm.doc.company;
            var scrubbedTitle = frm.doc.job_title
            var job_title = scrubbedTitle.toLowerCase().replace(/ /g, '-');
            // var company_name = scrubbedCompany.toLowerCase().replace(/ /g, '_');
            frm.doc.route_internal = "/" + job_title;
        }
        if (frm.doc.job_opening_category == "External"){
            frm.doc.publish = '0';
            frm.toggle_display("publish",true);
            frm.refresh_field('publish');
            frm.doc.custom_publish_internal = '0';
            frm.toggle_display("custom_publish_internal",false);
            frm.refresh_field('custom_publish_internal');
            frm.toggle_display("route_internal",false);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",false);
            frm.refresh_field('internal_job_route');
        }
        if (frm.doc.job_opening_category == ""){
            frm.doc.publish = '0';
            frm.toggle_display("publish",false);
            frm.refresh_field('publish');
            frm.doc.custom_publish_internal = '0';
            frm.toggle_display("custom_publish_internal",false);
            frm.refresh_field('custom_publish_internal');
            frm.toggle_display("route_internal",false);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",false);
            frm.refresh_field('internal_job_route');
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
        }
    },
    onload:function (frm){
        if (frm.doc.job_opening_category == ""){
            frm.doc.publish = '0';
            frm.toggle_display("publish",false);
            frm.refresh_field('publish');
            frm.doc.custom_publish_internal = '0';
            frm.toggle_display("custom_publish_internal",false);
            frm.refresh_field('custom_publish_internal');
            frm.toggle_display("route_internal",false);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",false);
            frm.refresh_field('internal_job_route');
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
        }
        if (frm.doc.custom_publish_internal == '1') {
            frm.doc.publish = '0';
            frm.toggle_display("publish",false);
            frm.refresh_field('publish');
            frm.doc.route='';
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
        }
        else{
            frm.toggle_display("route_internal",true);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",true);
            frm.refresh_field('internal_job_route');
        }
    },
    refresh: function (frm) {
        if (frm.doc.custom_publish_internal == '1') {
            // var scrubbedCompany = frm.doc.company;
            // var scrubbedTitle = frm.doc.job_title
            // var job_title = scrubbedTitle.toLowerCase().replace(/ /g, '-');
            // var company_name = scrubbedCompany.toLowerCase().replace(/ /g, '_');
            // frm.add_web_link("/internal_job/"+ company_name + "/" + job_title);
            frm.doc.publish = '0';
            frm.toggle_display("publish",false);
            frm.refresh_field('publish');
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
        }
        else{
            frm.toggle_display("route_internal",true);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",true);
            frm.refresh_field('internal_job_route');
        }
    },
    custom_publish_internal: function (frm) {
        if (frm.doc.custom_publish_internal == '1'){
            frm.toggle_display("route_internal",true);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",true);
            frm.refresh_field('internal_job_route');
        }
        else{
            frm.toggle_display("route_internal",false);
            frm.refresh_field('route_internal');
            frm.toggle_display("internal_job_route",false);
            frm.refresh_field('internal_job_route');
        }
    },
    publish:function(frm) {
        if (frm.doc.publish == '1'){
            frm.toggle_display("route",true);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",true);
            frm.refresh_field('job_application_route');
        }
        else{
            frm.toggle_display("route",false);
            frm.refresh_field('route');
            frm.toggle_display("job_application_route",false);
            frm.refresh_field('job_application_route');
        }
    },
    custom_all_employee:function(frm) {
        if (frm.doc.custom_all_employee == '1'){
            frm.doc.job_category = '';
            frm.toggle_display("job_category",false);
            frm.refresh_field('job_category');
        }
        else{
            frm.toggle_display("job_category",true);
            frm.refresh_field('job_category');
        }
        if (frm.doc.custom_all_employee == '0'){
            frm.doc.job_category = '';
            frm.toggle_display("job_category",true);
            frm.refresh_field('job_category');
        }
        else{
            frm.toggle_display("job_category",false);
            frm.refresh_field('job_category');
        }
    },
    job_category:function(frm) {
        if(frm.doc.job_category != ""){
            frm.toggle_display("custom_all_employee",false);
            frm.refresh_field('custom_all_employee');
        }
        else{
            frm.toggle_display("custom_all_employee",true);
            frm.refresh_field('custom_all_employee');
        }
    }
})