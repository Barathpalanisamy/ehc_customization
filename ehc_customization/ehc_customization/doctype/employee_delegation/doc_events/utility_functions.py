import frappe
import json
import frappe
from frappe import _
def update_new_employee_details(self):
    if not self.employee or not self.new_employee:
        frappe.throw(_("Current Employee and New Employee must be set"))
    current_emp_doc = frappe.get_doc("Employee", self.employee)
    new_emp_doc = frappe.get_doc("Employee", self.new_employee)
    new_emp_doc.reports_to = current_emp_doc.reports_to
    new_emp_doc.holiday_list = current_emp_doc.holiday_list
    new_emp_doc.ehc_accounting_department = current_emp_doc.ehc_accounting_department
    new_emp_doc.leave_approver = current_emp_doc.leave_approver
    new_emp_doc.default_shift = current_emp_doc.default_shift
    new_emp_doc.expense_approver = current_emp_doc.expense_approver    
    new_emp_doc.shift_request_approver = current_emp_doc.shift_request_approver
    new_emp_doc.save()
    # reports to
    reports_to=frappe.get_all("Employee",{"reports_to":current_emp_doc.name},pluck="name")
    for i in reports_to:
        report_doc=frappe.get_doc("Employee",i)
        report_doc.reports_to=self.new_employee
        report_doc.flags.ignore_mandatory = True
        report_doc.flags.ignore_permissions = True
        report_doc.save()
    # leave approver
    curr_userid = current_emp_doc.user_id
    new_userid = new_emp_doc.user_id
    leave_approver=frappe.get_all("Employee",{"leave_approver":curr_userid},pluck="name")
    for i in leave_approver:
        leave_doc=frappe.get_doc("Employee",i)
        leave_doc.leave_approver=new_userid
        leave_doc.flags.ignore_mandatory = True
        leave_doc.flags.ignore_permissions = True
        leave_doc.save()
    # expense_approver
    expense_approver=frappe.get_all("Employee",{"expense_approver":curr_userid},pluck="name")
    for i in expense_approver:
        expense_doc=frappe.get_doc("Employee",i)
        expense_doc.expense_approver=new_userid
        expense_doc.flags.ignore_mandatory = True
        expense_doc.flags.ignore_permissions = True
        expense_doc.save()
    # shift_request_approver
    shift_request_approver=frappe.get_all("Employee",{"shift_request_approver":curr_userid},pluck="name")
    for i in shift_request_approver:
        shift_doc=frappe.get_doc("Employee",i)
        shift_doc.shift_request_approver=new_userid
        shift_doc.flags.ignore_mandatory = True
        shift_doc.flags.ignore_permissions = True
        shift_doc.save()
        
def update_employee_references(self):
    old_employee_id = self.employee
    new_employee_id = self.new_employee

    for i in self.responsibility_details:
        fields = frappe.get_meta(i.property).fields
        employee_linked_fields = [field for field in fields if field.fieldtype == "Link" and field.options == "Employee"]
        for field in employee_linked_fields:
            # sql_query = """
            #     UPDATE `tab{doctype}`
            #     SET `{fieldname}` = '{new_employee_id}'
            #     WHERE `{fieldname}` = '{old_employee_id}'
            # """.format(doctype=i.property, fieldname=field.fieldname, old_employee_id=old_employee_id, new_employee_id=new_employee_id)
            # frappe.db.sql(sql_query)
            doctype = frappe.qb.DocType(i.property)
            (
                frappe.qb.update(doctype)
                .set(doctype[field.fieldname], new_employee_id)
                .where(doctype[field.fieldname] == old_employee_id)
            ).run()


        # Update fields fetched from Employee table
        for j in employee_linked_fields:
            employee_fetched_fields = [field for field in fields if field.fetch_from and field.fetch_from.startswith(j.fieldname)]
            for field in employee_fetched_fields:
                fetch_from_field = field.fetch_from.split('.')
                new_emp =frappe.get_value('Employee',new_employee_id,fetch_from_field[1])
                if new_emp:
                    # sql_query = """
                    #     UPDATE `tab{doctype}`
                    #     SET `{fieldname}` = '{fetch_field}'
                    # """.format(doctype=i.property, fieldname=field.fieldname, fetch_field =new_emp)
                    # frappe.db.sql(sql_query)
                    doctype = frappe.qb.DocType(i.property)

                    (
                    frappe.qb.update(doctype)
                    .set(doctype[field.fieldname], new_emp)
                ).run()
                    
@frappe.whitelist()
def designation_details(designation):
    des_doc=frappe.get_doc("Designation",designation)
    final_list=[]
    if des_doc.employee_responsibility:
        emp_des_doc=frappe.get_doc("Employee Responsibility",des_doc.employee_responsibility)
        for i in emp_des_doc.responsibility:
            final_list.append(i)
        return final_list
    else:
        return final_list

@frappe.whitelist()
def transfer_details_updation(doc):
    doc=json.loads(doc)
    des_doc=frappe.get_doc("Designation",doc.get("designation"))
    emp_des_doc=frappe.get_doc("Employee Responsibility",des_doc.employee_responsibility)
    emp_des_doc.responsibility=[]
    des_doc.transfer_details=[]
    for i in doc.get("responsibility_details"):
        des_doc.append('transfer_details',{"property": i.get("property"),"type":i.get("type")})
        emp_des_doc.append("responsibility", {"property": i.get("property"),"type":i.get("type")})
    emp_des_doc.flags.ignore_mandatory = True
    emp_des_doc.flags.ignore_permissions= True
    emp_des_doc.save()
    des_doc.save()

    
