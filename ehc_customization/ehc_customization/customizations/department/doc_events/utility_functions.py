import frappe
from frappe import _
import json
import requests
import urllib.parse
from frappe.utils import now
from frappe.frappeclient import FrappeClient

def validate(self, event):
    if self.ehc_manager_national_id:
        employee_id = frappe.get_all('Employee', filters={'nat_id': self.ehc_manager_national_id})
        if employee_id:
            self.custom_reports_to = employee_id[0]['name']
            employees = frappe.get_all('Employee', filters={'department': self.name})
            for employee in employees:
                emp =frappe.get_doc("Employee",employee.name)
                if not emp.name ==self.custom_reports_to and emp.manager_type == "Direct Manager":
                    reports_emp = frappe.get_doc("Employee",self.custom_reports_to)
                    emp.reports_to = self.custom_reports_to
                    emp.expense_approver = reports_emp.user_id
                    emp.leave_approver = reports_emp.user_id
                    emp.shift_request_approver = reports_emp.user_id
                    emp.save()


def transfer_entry(self, method=None):
    try:
        target_site, file_hosting_records = site_details()

        auth_response = requests.post(
            f"{target_site['url']}/api/method/login",
            data={'usr': target_site['user'], 'pwd': file_hosting_records.target_key}, verify=False
        )

        data = self.__dict__
        if method == 'after_insert':
            data1 = {}
            for key, value in data.items():
                if type(value) == str:
                    data1[key] = value
            create_sync(data1, type='Create')
            
        elif method == 'on_update':
            try:
                if data['flags']['in_insert']:
                    return
            except:
                create_sync(data, type='Update')

        elif method == 'on_trash':
            create_sync(data, type='Delete')
    except:
        frappe.log_error(message=frappe.get_traceback(), title="File Hosting Error")

def site_details():
    file_hosting_records = frappe.get_doc('Server Hosting')
    docSettings = frappe.get_single("Server Hosting")
    source = docSettings.get_password('secret_key')
    target = docSettings.get_password('target_key')
    file_hosting_records.secret_key = source
    file_hosting_records.target_key = target
    target_site = {
            'url': file_hosting_records.target_url,
            'user': file_hosting_records.target_id,
            'password': file_hosting_records.target_key
        }
    return target_site, file_hosting_records

set_of_fields = ['gender', 'salutation', 'department', 'employment_type',\
                         'designation', 'branch', 'employee_grade', 'job_speciality', 'nationality', 'company']


def create_sync(data, type):    
    try:
        create_sync = frappe.new_doc('Sync Status Log')
        create_sync.update_type = type
        create_sync.document_type = data['doctype']
        create_sync.document_name = data['name']
        if type == 'Create':
            create_sync.data = data
        elif type == 'Delete':
            create_sync.data = {'doctype':data['doctype'],'name':data['name']}
        create_sync.save()
        create_sync.submit()

    except Exception as err:
        frappe.log_error(message=err, title="Sync Error")

def create_entry(target_site, data, auth_response):
    try:
        client = FrappeClient(target_site['url'], target_site['user'], target_site['password'], verify=False)

        data = create_dependencies(client, data, target_site, auth_response)
        employee = client.insert(data)
        return employee

    except Exception as err:
        frappe.log_error(message=err, title="Sync Error")

def update_entry(self, data, target_site, auth_response):
    try:
        del data['creation'] 
        client = FrappeClient(target_site['url'], target_site['user'], target_site['password'], verify=False)

        data1 = create_dependencies(client, data, target_site, auth_response)
        data = child_table_update(data1, target_site, auth_response)

        response = requests.get(f"{target_site['url']}/api/resource/{data['doctype']}/{urllib.parse.quote(data['name'])}", cookies=auth_response.cookies, verify=False)
        if response.status_code != 200:
            if (self.doctype == 'ToDo' and self.status == 'Cancelled'):
                update_and_remove_attachments(self, data, target_site, auth_response)
            return response
        if response.status_code == 200:
            datas = response.json()['data']['modified']
            data['modified'] = datas
            del data['modified_by']
            del data['owner']
            if data['name'] == response.json()['data']['name']:
                try:
                    response = requests.put(
                            f"{target_site['url']}/api/resource/{data['doctype']}/{urllib.parse.quote(data['name'])}",
                            data=data,
                            cookies=auth_response.cookies, verify=False         
                        )
                    return response
                except Exception as err:
                    frappe.log_error(message=err, title="Sync Error")
                    self.reload()
        self.reload()

    except Exception as err:
        frappe.log_error(message=err, title="Sync Error")
        self.reload()

def delete_entry(target_site, data, auth_response):
    response = requests.delete(
                f"{target_site['url']}/api/resource/{data['doctype']}/{urllib.parse.quote(data['name'])}",
                cookies=auth_response.cookies, verify=False          
            )
    return response

def rename_doc(target_site, doctype, old_name, new_name, auth_response):
    params = {
        'cmd': 'frappe.client.rename_doc',
        'doctype': doctype,
        'old_name': new_name,
        'new_name': old_name,
    }
    requests.put(
                f"{target_site['url']}/api/resource/{doctype}",
                data=params,
                cookies=auth_response.cookies,
                verify=False     
            )
def update_and_remove_attachments(self, target_site, auth_response):
    filters = ({
        'reference_type': self.reference_type,
        'reference_name': self.reference_name,
        'allocated_to': self.allocated_to,
    })
    filters_json = json.dumps(filters)
    response = requests.get(
                f"{target_site['url']}/api/resource/{self.doctype}",
                params={'filters': filters_json},
                cookies=auth_response.cookies,verify=False    
            )
    if response.status_code == 200:
        response = requests.put(
        f"{target_site['url']}/api/resource/{self.doctype}/{response.json()['data'][0]['name']}",
        json={'status': 'Cancelled'},
        cookies=auth_response.cookies,verify=False 
    )
        
def child_table_update(data, target_site, auth_response):
    try:
        if len(data['_table_fieldnames']) > 0:
            for i in data['_table_fieldnames']:
                if data[i]:
                    response = requests.get(
                        f"{target_site['url']}/api/resource/Employee/{data['name']}",
                        cookies=auth_response.cookies,verify=False
                    )
                    if response.status_code == 200:
                        existing_data = response.json()['data'][i]
                        
                        existing_data_map = {item['idx']: item for item in existing_data}
                        for index, col in enumerate(data[i]):
                            col = col.__dict__
                            if col['idx'] in existing_data_map:
                                col['name'] = existing_data_map[col['idx']]['name']
                                del col['creation']
                                del col['modified']
                                response = requests.put(
                                    f"{target_site['url']}/api/resource/{existing_data_map[col['idx']]['doctype']}/{urllib.parse.quote(existing_data_map[col['idx']]['name'])}",
                                    data=col,
                                    cookies=auth_response.cookies,verify=False
                                )
                            else:
                                response = requests.post(
                                    f"{target_site['url']}/api/resource/{col['doctype']}",
                                    data=col,
                                    cookies=auth_response.cookies,verify=False
                                )
                        
                        data_names = {col.__dict__['idx'] for col in data[i]}
                        for existing_item in existing_data:
                            if existing_item['idx'] not in data_names:
                                response = requests.delete(
                                    f"{target_site['url']}/api/resource/{existing_item['doctype']}/{urllib.parse.quote(existing_item['name'])}",
                                    cookies=auth_response.cookies,verify=False
                                )
                        
                        del data[i]
                else:
                    data[i] = []
    except Exception as err:
        frappe.log_error(message=err, title="Sync Error")

    return data

def create_dependencies(client, data, target_site, auth_response):
    doctype_metadata = frappe.get_meta(data['doctype'])
    link_fields = [
        field for field in doctype_metadata.fields
        if field.get('fieldtype') == 'Link'
    ]
    for link in link_fields:
        if data[link.fieldname]:
            verify = requests.get(f"{target_site['url']}/api/resource/{link.get('options')}/{(data[link.get('fieldname')])}", cookies=auth_response.cookies,verify=False)
            if verify.status_code == 404:
                if link.get('fieldname') in set_of_fields:
                    get_doc = frappe.get_doc(link.get('options'), data[link.get('fieldname')])
                    if get_doc:
                        try:
                            employee = client.insert(get_doc)
                        except Exception as err:
                            del data[link.get('fieldname')]
                else:
                    del data[link.get('fieldname')]
    return data

@frappe.whitelist()
def call_event_streaming():
    target_site, file_hosting_records = site_details()
    auth_response = requests.post(
            f"{target_site['url']}/api/method/login",
            data={'usr': target_site['user'], 'pwd': file_hosting_records.target_key},verify=False
        )
    try:
        doctype = set_of_fields
        for id in doctype:
            get_list = frappe.get_list(id, {}, pluck='name')
            for item in get_list:
                verify = requests.get(f"{target_site['url']}/api/resource/{id}/{item}", cookies=auth_response.cookies,verify=False)
                if verify.status_code == 404:
                    get_doc = frappe.get_doc(id, item)
                    if get_doc:
                        create_items = create_entry(target_site, get_doc.__dict__, auth_response)
    except Exception as err:
        frappe.log_error(message=err, title="Sync Error")

@frappe.whitelist()
def sync_between_servers():
    get_sync_data = frappe.get_all('Sync Status Log', filters={'docstatus': 1, 'status_code': ['!=', 'Synced']}, fields=['*'], order_by='creation asc')
    target_site, file_hosting_records = site_details()

    auth_response = requests.post(
        f"{target_site['url']}/api/method/login",
        data={'usr': target_site['user'], 'pwd': file_hosting_records.target_key},verify=False
    )
    if get_sync_data:
        
        for log in get_sync_data:
            try:   
                if len(frappe.get_all(log['document_type'], {'name':log['document_name']},['*'])):                 
                    get_doc = frappe.get_doc(log['document_type'], log['document_name'])
                    if get_doc:
                        doc = frappe.get_doc('Sync Status Log', log['name'])
                        if log['update_type'] == 'Create':
                            values = get_doc.__dict__
                            for key, value in (json.loads(log['data'])).items():
                                values[key] = value
                            response = create_entry(target_site, values, auth_response) 
                            doc = update_log(doc, response)

                        elif log['update_type'] == 'Update':
                            response = update_entry(get_doc, get_doc.__dict__, target_site, auth_response)
                            doc = update_log(doc, response)
                        elif log['update_type'] == 'Delete':
                            response = delete_entry(target_site, get_doc.__dict__, auth_response)
                            doc = update_log(doc, response)
                        doc.save(ignore_permissions=True)
                        frappe.db.commit()
                else:
                    doc = frappe.get_doc('Sync Status Log', log['name'])
                    if log['update_type'] == 'Delete':
                        response = delete_entry(target_site, json.loads(log['data']), auth_response)
                        doc = update_log(doc, response)
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
            
            except Exception as err:
                print(err)

def update_log(doc, response):
    try:
        if response.status_code in [200, 202 ]:
            doc.status_code = 'Synced'
            doc.last_sync = now()
            doc.response = str(response._content)
        elif response.name:
            doc.status_code = 'Synced'
            doc.last_sync = now()
            doc.response = response
        else:
            doc.response = str(response)
    except Exception as e:
        doc.status_code =  'Failed'
        doc.response = str(response._content)
    return doc
