import frappe

@frappe.whitelist()
def get_additional_fields(doctype):
    additional_fields = frappe.get_meta(doctype).get("fields")
    fields =[' '] + [field.label for field in additional_fields if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']]
    return fields

@frappe.whitelist()
def get_fields(source, target):
    source_fields_meta = frappe.get_meta(source).get("fields")
    source_fields = [
        {"label": field.label, "fieldname": field.fieldname}
        for field in source_fields_meta
        if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']
    ]
    
    target_fields_meta = frappe.get_meta(target).get("fields")
    target_fields = [
        {"label": field.label, "fieldname": field.fieldname}
        for field in target_fields_meta
        if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']
    ]
    
    matched_fields_values = []
    for source_field in source_fields:
        for target_field in target_fields:
            if (source_field['label'].lower() in target_field['label'].lower() or
                target_field['label'].lower() in source_field['label'].lower()):
                matched_fields_values.append({
                    "source_label": source_field['label'],
                    "source_fieldname": source_field['fieldname'],
                    "target_label": target_field['label'],
                    "target_fieldname": target_field['fieldname']
                })
             
    return matched_fields_values

@frappe.whitelist()
def get_fieldname(doctype, field_type):
    doctype_fields_meta = frappe.get_meta(doctype).get("fields")
    doctype_fields = [
        {"label": field.label, "fieldname": field.fieldname}
        for field in doctype_fields_meta
        if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break']
    ]
    for doctype_field in doctype_fields:
        if(doctype_field['label'] == field_type):
            matched_value = doctype_field['fieldname']
    
    return matched_value