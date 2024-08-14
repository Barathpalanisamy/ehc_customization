frappe.ui.form.on("Work Experience",{
    from_date:function(frm){
        updateExperienceYears(frm);

    },
    to_date:function(frm){
        updateExperienceYears(frm);
        
    },
    current:function(frm){
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

    for (var i = 0; i < frm.doc.experience_details.length; i++) {
        var row = frm.doc.experience_details[i];
        var startDate = new Date(row.from_date);
        var endDate = new Date(row.to_date);
        if (row.current ==1) {
            endDate = new Date(); 
        }
            
            if (startDate < endDate) {
                var difference = differenceInYears(startDate, endDate);
                totalYearsNoOverlap += difference;
    
                var overlapDetected = false;
    
                for (var j = 0; j < i; j++) {
                    var prevRow = frm.doc.experience_details[j];
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
    
    frm.set_value('overlap_experience_in_years',totalYearsWithOverlap)
   
    var totalexp=totalYearsNoOverlap - totalYearsWithOverlap
    totalexp=parseFloat(totalexp.toFixed(1))

    frm.set_value('experience_years',totalexp );
}
