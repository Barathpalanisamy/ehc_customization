import frappe
from frappe import _

def percentage_validation(self):
    total_percentage=0
    total_percentage+=self.goal_score_percentage
    total_percentage+=self.feedback_percentage
    total_percentage+=self.self_rating_percentage
    if total_percentage > 100:
        frappe.throw(_("Total Allocate Percentage add up to 100."))