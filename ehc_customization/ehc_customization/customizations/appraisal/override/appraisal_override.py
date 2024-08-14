import frappe
from frappe import _
from frappe.utils import flt
from frappe.query_builder.functions import Avg


def set_goal_score(self, update=False):
		for kra in self.appraisal_kra:
			# update progress for all goals as KRA linked could be removed or changed
			Goal = frappe.qb.DocType("Goal")
			avg_goal_completion = (
				frappe.qb.from_(Goal)
				.select(Avg(Goal.progress).as_("avg_goal_completion"))
				.where(
					(Goal.kra == kra.kra)
					& (Goal.employee == self.employee)
					# archived goals should not contribute to progress
					& (Goal.status != "Archived")
					& ((Goal.parent_goal == "") | (Goal.parent_goal.isnull()))
					& (Goal.appraisal_cycle == self.appraisal_cycle)
				)
			).run()[0][0]

			kra.goal_completion = flt(avg_goal_completion, kra.precision("goal_completion"))
			kra.goal_score = flt(kra.goal_completion * kra.per_weightage / 100, kra.precision("goal_score"))

			if update:
				kra.db_update()

		self.calculate_total_score()

		if update:
			self.calculate_final_score()
			self.db_update()

		return self
	
def calculate_total_score(self):
	total_weightage, total, goal_score_percentage = 0, 0, 0

	if self.rate_goals_manually:
		table = _("Goals")
		self.goal_score_earned_percentage=0
		for entry in self.goals:
			if flt(entry.score) > 5:
				frappe.throw(_("Row {0}: Goal Score cannot be greater than 5").format(entry.idx))	
			entry.score_earned = flt(entry.score) * flt(entry.per_weightage) / 100
			total += flt(entry.score_earned)
			entry.total_allocate_percentage=flt(entry.score_earned)/5*100
			self.goal_score_earned_percentage +=entry.total_allocate_percentage
			total_weightage += flt(entry.per_weightage)

	else:
		table = _("KRAs")
		for entry in self.appraisal_kra:
			goal_score_percentage += flt(entry.goal_score)
			total_weightage += flt(entry.per_weightage)

		self.goal_score_percentage = flt(goal_score_percentage, self.precision("goal_score_percentage"))
		# convert goal score percentage to total score out of 5
		total = flt(goal_score_percentage) / 20

	if total_weightage and flt(total_weightage, 2) != 100.0:
		frappe.throw(
			_("Total weightage for all {0} must add up to 100. Currently, it is {1}%").format(
				table, total_weightage
			),
			title=_("Incorrect Weightage Allocation"),
		)
	self.total_score = flt(total, self.precision("total_score"))

def calculate_avg_feedback_score(self, update=False):
		avg_feedback_score = frappe.qb.avg(
			"Employee Performance Feedback",
			"total_score",
			{"employee": self.employee, "appraisal": self.name, "docstatus": 1},
		)

		self.avg_feedback_score = flt(avg_feedback_score, self.precision("avg_feedback_score"))
		self.avg_earned_percentage=flt(self.avg_feedback_score)/5*100
		if update:
			self.calculate_final_score()
			self.db_update()

def calculate_self_appraisal_score(self):
	total = 0
	self.self_earned_percentage=0
	for entry in self.self_ratings:
		if frappe.db.get_single_value("Appraisal Settings", "self_rating_percentage"):
				entry.total_self_allocate_percentage=frappe.db.get_single_value("Appraisal Settings", "self_rating_percentage")

		score = flt(entry.rating) * 5 * flt(entry.per_weightage / 100)
		entry.total_self_allocate_percentage=flt(score)/5*100
		self.self_earned_percentage+=entry.total_self_allocate_percentage
		total += flt(score)
	self.self_score = flt(total)


def calculate_final_score(self):
	total_score,self_score,avg_feedback_score=0,0,0
	goal_score_percentage=flt(frappe.db.get_single_value("Appraisal Settings", "goal_score_percentage"))
	feedback_percentage=flt(frappe.db.get_single_value("Appraisal Settings", "feedback_percentage"))
	self_rating_percentage=flt(frappe.db.get_single_value("Appraisal Settings", "self_rating_percentage"))

	if goal_score_percentage:
		self.goal_score_allocate_percentage=goal_score_percentage
		total_score=flt(self.total_score)*(flt(goal_score_percentage)/100)

	if feedback_percentage:
		avg_feedback_score=(flt(self.avg_feedback_score)*(flt(feedback_percentage)/100))
	
	if self_rating_percentage:
		self.self_allocate_percentage=self_rating_percentage
		self_score=(flt(self.self_score))*(flt(self_rating_percentage)/100)

	if goal_score_percentage and feedback_percentage and self_rating_percentage:
		final_score = (flt(total_score) + flt(avg_feedback_score) + flt(self_score))
		self.total_earned_percentage=flt(final_score/5*100)

	elif not (goal_score_percentage and feedback_percentage and self_rating_percentage):
		frappe.throw(_("Fill Allocate Percentage In Appraisal Settings"))
		
	else:
		final_score = (flt(total_score) + flt(avg_feedback_score) + flt(self_score)) / 3

	self.final_score = flt(final_score, self.precision("final_score"))

