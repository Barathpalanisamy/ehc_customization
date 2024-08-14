frappe.ui.form.on("Attendance", {
    refresh: function(frm){
        frm.trigger("add_custom_connections_resignation")
    },
    add_custom_connections_resignation(frm){
        if(frm.is_new()){
            return
        }
        let show_connections = false
        let count_tag = $(frm.dashboard.transactions_area).find(".attendance-request-count")
        if(count_tag){
            count_tag.removeClass("hidden")
        }
        let connection_html = `
            <div class="document-link-badge hidden attendance-request-link" data-doctype="Attendance Request">
                <span class="count attendance-request-count">1</span>
                <a class="badge-link" href="/app/attendance-request/${frm.doc.custom_attendance}">Attendance Request</a>
            </div>
        `
        let div = document.createElement("div")
        div.setAttribute("class", "document-link")
        div.setAttribute("data-doctype", "Attendance Request")
        div.innerHTML = connection_html
        if(!frm.emp_reg_connections_added){
            let connection_column = $(frm.dashboard.transactions_area).find(".col-md-4")
            if(!connection_column || (connection_column && !connection_column.length)){
                connection_column = frm.dashboard.transactions_area
            }
            if(frm.doc.custom_attendance){
                connection_column.append(div)
                frm.emp_reg_connections_added = true
            }
        }
        let exit_int_link = $(frm.dashboard.transactions_area).find(".attendance-request-link")
        if(frm.doc.custom_attendance){
            exit_int_link.removeClass("hidden")
            show_connections = true
        }
        if(show_connections){
            frm.$wrapper.find(".form-dashboard").find(".form-links").removeClass("hide-control")
        }
    }
})