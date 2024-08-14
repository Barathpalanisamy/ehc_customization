import frappe
from frappe.utils import today


def update_temporary_employee():
        emp_del = frappe.get_all("Employee Delegation",{'transfer_type':"Temporary","to_date":today()},pluck='name')
        for i in emp_del:
            doc = frappe.get_doc("Employee Delegation",i)
    
            old_employee_id = doc.new_employee
            new_employee_id = doc.employee 

            for i in doc.responsibility_details:
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
