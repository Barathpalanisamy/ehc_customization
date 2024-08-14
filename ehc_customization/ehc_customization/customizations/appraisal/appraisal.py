import frappe
from ehc_customization.ehc_customization.customizations.appraisal.override.appraisal_override import(
calculate_avg_feedback_score,
set_goal_score,
calculate_total_score,
calculate_self_appraisal_score,
calculate_final_score
)
from hrms.hr.doctype.appraisal.appraisal import Appraisal

class AppraisalCalculation(Appraisal):
    def validate(self):
        set_goal_score(self)
        calculate_total_score(self)
        calculate_avg_feedback_score(self)
        calculate_self_appraisal_score(self)
        calculate_final_score(self)
        
