import frappe
from frappe import _
from datetime import datetime

def override_salary_components(doc):
    extra_comp=[]
    earnings=[]
    salary_sum_ded=0
    salary_sum_ear=0
    total_gross=0
    total_ded=0
    deductions=[]
    all_add_salary=[]
    final_text=""
    payroll_entry=frappe.get_doc("Payroll Entry",doc.payroll_entry)

    if payroll_entry.custom_payroll_type_ehc:
        doc.earnings=[]
        doc.deductions=[]

        payroll_type=frappe.get_doc("Payroll Type",payroll_entry.custom_payroll_type_ehc)
        for i in payroll_type.salary_component:
            extra_comp.append(i.salary_component)

        for j in extra_comp:
            salary_sum_ear=0
            comp_type=frappe.get_value("Salary Component",j,"type")
            if comp_type == "Earning":
                add_salary=frappe.get_all("Additional Salary",{"custom_paid_additional_salary":0,"salary_component":j,"employee":doc.employee,"docstatus":["!=",2]},pluck="name")
                for k in add_salary:
                    all_add_salary.append(k)
                    add_doc=frappe.get_doc("Additional Salary",k)
                    salary_sum_ear+=add_doc.amount
                    
                
                total_gross+=salary_sum_ear
                
                if salary_sum_ear != 0:
                    earnings.append({
                        "salary_component": j,
                        "amount": salary_sum_ear
                
                    })
                else:
                    doc.gross_pay=0

            if comp_type == "Deduction":
                salary_sum_ded=0
                add_salary=frappe.get_all("Additional Salary",{"custom_paid_additional_salary":0,"salary_component":j,"employee":doc.employee,"docstatus":["!=",2]},pluck="name")
                for k in add_salary:
                    all_add_salary.append(k)
                    add_doc=frappe.get_doc("Additional Salary",k)
                    salary_sum_ded+=add_doc.amount
                    final_text += f"{j} - {add_doc.amount}\n"

                total_ded+=salary_sum_ded
                if salary_sum_ded != 0:
                    deductions.append({
                        "salary_component": j,
                        "amount": salary_sum_ded
                
                    })
                else:
                    doc.total_deduction=0
        
        if earnings:
            doc.gross_pay=total_gross
            doc.gross_year_to_date=total_gross
            doc.update({
                "earnings":earnings
            })
        if deductions:
            doc.total_deduction=total_ded
            doc.update({
                "deductions":deductions
            })
        #else:
            #frappe.throw(_("No additional Slary this employee {0}".format(doc.employee)))

       



def change_paid_status(doc):
    extra_comp=[]
    all_add_salary=[]
    final_text=""
    payroll_entry=frappe.get_doc("Payroll Entry",doc.payroll_entry)
    if payroll_entry.custom_payroll_type_ehc:
        payroll_type=frappe.get_doc("Payroll Type",payroll_entry.custom_payroll_type_ehc)
        for i in payroll_type.salary_component:
            extra_comp.append(i.salary_component)
        for j in extra_comp:
            salary_sum_ear=0
            comp_type=frappe.get_value("Salary Component",j,"type")
            if comp_type == "Earning":
                add_salary=frappe.get_all("Additional Salary",{"custom_paid_additional_salary":0,"salary_component":j,"employee":doc.employee,"docstatus":["!=",2]},pluck="name")
                for k in add_salary:
                    all_add_salary.append(k)
                    add_doc=frappe.get_doc("Additional Salary",k)
                    salary_sum_ear+=add_doc.amount
                    month_name = add_doc.payroll_date.strftime('%b')
                    final_text += f"{j}({month_name}) - {add_doc.amount} + "
                final_text = final_text.rstrip(' + ')
                final_text += f" = {salary_sum_ear},\n"

                   

            if comp_type == "Deduction":
                salary_sum_ded=0
                add_salary=frappe.get_all("Additional Salary",{"custom_paid_additional_salary":0,"salary_component":j,"employee":doc.employee,"docstatus":["!=",2]},pluck="name")
                for k in add_salary:
                    all_add_salary.append(k)
                    add_doc=frappe.get_doc("Additional Salary",k)
                    salary_sum_ded+=add_doc.amount
                    month_name = add_doc.payroll_date.strftime('%b') 
                    final_text += f"{j}({month_name}) - {add_doc.amount} + "
                final_text = final_text.rstrip(' + ')
                final_text += f" = {salary_sum_ded},\n"


        doc.add_comment(text=final_text)
        for j in all_add_salary:
            frappe.db.set_value("Additional Salary",j,"custom_paid_additional_salary",1)
            frappe.db.set_value("Additional Salary",j,"custom_salary_slip",doc.name)
            frappe.db.set_value("Additional Salary",j,"custom_payroll_entry",doc.payroll_entry)
            
def change_paid_status_to_none(doc):
    add_salary = frappe.get_all("Additional Salary",{"custom_salary_slip":doc.name,"custom_paid_additional_salary":1,"docstatus": ["!=", 0]},pluck='name')
    for i in add_salary:
        frappe.db.set_value("Additional Salary",i,"custom_paid_additional_salary",0)
        frappe.db.set_value("Additional Salary",i,"custom_salary_slip",'')
        frappe.db.set_value("Additional Salary",i,"custom_payroll_entry",'')
            
