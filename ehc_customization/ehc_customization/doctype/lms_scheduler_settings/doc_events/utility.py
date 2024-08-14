import frappe
import datetime


def update_frequency(doc, method):
    if doc.scheduler_frequency:
        get_doc = frappe.get_doc('Scheduled Job Type', 'utility_functions.sync_between_servers')
        if doc.scheduler_frequency == 'Cron':
            get_cron_format = generate_cron_schedule(int(doc.cron_time))
            get_doc.cron_format =  get_cron_format
        else:
            get_doc.cron_format =  ''
        get_doc.last_execution = datetime.datetime.now()
        get_doc.frequency = doc.scheduler_frequency
        get_doc.save()
        
def generate_cron_schedule(minutes_interval):
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    if minutes_interval == 0:
        return f"{current_minute} {current_hour} * * *"
    elif minutes_interval < 60:
        return f"{current_minute % minutes_interval}/{minutes_interval} * * * *"
    else:
        mins_to_hr = datetime.timedelta(minutes=minutes_interval)
        next_time = current_time + datetime.timedelta(minutes=minutes_interval)
        next_hour = next_time.hour
        next_minute = next_time.minute
        total_hours = mins_to_hr.total_seconds() // 3600
        return f"{next_minute} {current_hour + int(total_hours)}/{int(total_hours)} * * *"