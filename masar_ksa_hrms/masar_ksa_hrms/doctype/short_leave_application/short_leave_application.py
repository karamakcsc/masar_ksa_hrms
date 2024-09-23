# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime, timedelta

class ShortLeaveApplication(Document):
    def validate(self):
        self.shift_validate()
    def on_submit(self):
        self.calculate_leave_application()
    def calculate_leave_application(self):
        total_of_duration_before_this_leave = 0 
        if self.balance_deduction and self.status == "Approved":
            if float(self.leave_duration) > 0 :
                if self.employee:
                    hr_settings_doc = frappe.get_doc('HR Settings')
                    standard_working_hours = float(hr_settings_doc.standard_working_hours)
                    if standard_working_hours not in [0 , None]:
                        hours = int(standard_working_hours)
                        minutes = int((standard_working_hours - hours) * 60)
                        swh_in_seconds = hours * 3600 + minutes * 60
                        application_duration_sql = frappe.db.sql("""
                                SELECT 
                                    name , 
                                    application_duration 
                                FROM `tabShort Leave Application` tsla 
                            WHERE 
                                docstatus = 1 
                                AND status ='Approved' 
                                AND balance_deduction =1 
                                AND to_calaculate = 1 
                                AND employee = %s""" , (self.employee) , as_dict=True)
                        if len(application_duration_sql) !=0:
                            for app_dur in application_duration_sql:
                                total_of_duration_before_this_leave += float(app_dur.application_duration)
                            total_of_duration = total_of_duration_before_this_leave + float(self.leave_duration)
                            if total_of_duration > swh_in_seconds:
                                new_leave_app_doc = frappe.new_doc('Leave Application')
                                new_leave_app_doc.employee = self.employee
                                new_leave_app_doc.employee_name = self.employee_name
                                new_leave_app_doc.leave_type = self.leave_type
                                new_leave_app_doc.company = self.company
                                new_leave_app_doc.department = self.department
                                new_leave_app_doc.from_date = self.leave_date
                                new_leave_app_doc.to_date = self.leave_date
                                new_leave_app_doc.total_leave_days = 1 
                                new_leave_app_doc.leave_approver = self.leave_approver
                                new_leave_app_doc.posting_date = self.leave_date
                                new_leave_app_doc.status ="Approved"
                                new_leave_app_doc.custom_sla_reference = self.name 
                                new_leave_app_doc.insert(ignore_permissions=True)
                                new_leave_app_doc.submit()
                                application_duration = total_of_duration -swh_in_seconds
                                self.application_duration = application_duration
                                self.to_calaculate =1 
                                self.calculated = 0 
                                for docs in application_duration_sql:
                                    edit_doc = frappe.get_doc('Short Leave Application' , docs.name)
                                    edit_doc.calculated = 1 
                                    edit_doc.to_calaculate = 0 
                                    edit_doc.application_duration = docs.application_duration
                                    edit_doc.save()
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'calculated' ,  1 )
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'to_calaculate' ,  0 )
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'application_duration' , docs.application_duration )
                                frappe.db.set_value('Short Leave Application' , self.name , 'application_duration' , self.leave_duration)
                                frappe.db.set_value('Short Leave Application' , self.name , 'calculated' , 0)
                                frappe.db.set_value('Short Leave Application' , self.name , 'to_calaculate' ,1)
                                frappe.msgprint(
                                        "The Leave Application has been Successfully Created and Submitted.",
                                        alert=True,
                                        indicator='green'
                                    )

                            elif total_of_duration < swh_in_seconds:
                                self.application_duration = self.leave_duration
                                self.to_calaculate =1 
                                self.calculated = 0 
                                frappe.db.set_value('Short Leave Application' , self.name , 'application_duration' , self.leave_duration)
                                frappe.db.set_value('Short Leave Application' , self.name , 'calculated' , 0)
                                frappe.db.set_value('Short Leave Application' , self.name , 'to_calaculate' ,1)
                            elif total_of_duration == swh_in_seconds:
                                new_leave_app_doc = frappe.new_doc('Leave Application')
                                new_leave_app_doc.employee = self.employee
                                new_leave_app_doc.employee_name = self.employee_name
                                new_leave_app_doc.leave_type = self.leave_type
                                new_leave_app_doc.company = self.company
                                new_leave_app_doc.department = self.department
                                new_leave_app_doc.from_date = self.leave_date
                                new_leave_app_doc.to_date = self.leave_date
                                new_leave_app_doc.total_leave_days = 1 
                                new_leave_app_doc.leave_approver = self.leave_approver
                                new_leave_app_doc.posting_date = self.leave_date
                                new_leave_app_doc.status ="Approved"
                                new_leave_app_doc.custom_sla_reference = self.name 
                                new_leave_app_doc.insert(ignore_permissions=True)
                                new_leave_app_doc.submit()
                                self.application_duration = self.leave_duration
                                self.calculated = 1 
                                self.to_calaculate = 0 
                                for docs in application_duration_sql:
                                    edit_doc = frappe.get_doc('Short Leave Application' , docs.name)
                                    edit_doc.calculated = 1 
                                    edit_doc.to_calaculate = 0 
                                    edit_doc.application_duration = docs.application_duration
                                    edit_doc.save()
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'calculated' , 1)
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'to_calaculate' , 0)
                                    frappe.db.set_value('Short Leave Application' , docs.name , 'application_duration' ,docs.application_duration)
                                frappe.db.set_value('Short Leave Application' , self.name , 'application_duration' , self.leave_duration)
                                frappe.db.set_value('Short Leave Application' , self.name , 'calculated' , 1)
                                frappe.db.set_value('Short Leave Application' , self.name , 'to_calaculate' ,0)
                                frappe.msgprint(
                                    "The Leave Application has been Successfully Created and Submitted.",
                                    alert=True,
                                    indicator='green'
                                )
                        else:
                            self.application_duration = self.leave_duration
                            self.to_calaculate =1 
                            self.calculated = 0 
                            frappe.db.set_value('Short Leave Application' , self.name , 'to_calaculate' , 1)
                            frappe.db.set_value('Short Leave Application' , self.name , 'calculated' , 0)
                            frappe.db.set_value('Short Leave Application' , self.name , 'application_duration' ,self.leave_duration)
                    else:
                        frappe.throw("""Standard Working Hours have not been defined in the HR Settings. 
                                     Please enter the required working hours to proceed.""" , title=_("Standard Working Hours"))
                else:
                    frappe.throw("Set Employee" , title=_("Missing Employee"))

            else:
                frappe.throw("Leave duration cannot be zero. Please enter a valid leave duration." , title=_("Missing Leave Duration"))
    @frappe.whitelist()
    def get_start_end_shift(self):
        if self.shift_start or self.end_shift:
            shift_time_sql = frappe.db.sql("""
                            SELECT 
                                start_time , end_time
                            FROM `tabShift Type` tst 
                            INNER JOIN `tabShift Assignment` tsa ON tsa.shift_type = tst.name
            WHERE tsa.name = %s""" , (self.shift_assignment) , as_dict=True)
            if self.shift_start: 
                from_time = shift_time_sql[0]['start_time']
                to_time = None
            if self.end_shift:
                to_time = shift_time_sql[0]['end_time']
                from_time = shift_time_sql[0]['start_time'] 
            return {
            'from_time' : from_time,
            'to_time' : to_time
            }

    @frappe.whitelist()
    def calculate_durations(self):
        leave_duration = int(self.leave_duration) if self.leave_duration else 0
        duration_delta = timedelta(seconds=leave_duration)
        time_format = "%H:%M:%S"
       
        if self.shift_start:
            from_time = datetime.strptime(self.from_time, time_format)
            to_time = (from_time + duration_delta).time()
            return {
            'from_time' : self.from_time,
            'to_time' : to_time 
            }
        elif self.end_shift:
            to_time = datetime.strptime(self.to_time, time_format)
            from_time = (to_time  - duration_delta).time()
            self.from_time = from_time.strftime(time_format) 
            return {
            'from_time' : self.from_time,
            'to_time' : self.to_time 
            }
        elif self.in_shift:
            from_time = datetime.strptime(self.from_time, time_format)
            to_time = (from_time + duration_delta).time()
            return {
            'from_time' : self.from_time,
            'to_time' : to_time 
            }
            
    def shift_validate(self):
        if (self.salary_deduction + self.balance_deduction + self.none_deduction )!= 1:
            frappe.throw("""At least one of the following must be selected:
                         <br>
                         <ul>
                            <li><b> Salary Deduction </b></li> 
                            <li><b> Balance Deduction </b></li>
                            <li><b> None Deduction </b></li> 
                        </ul>""" , title=_("Missing Deduction Type"))
        if (self.shift_start +self.end_shift +self.in_shift) != 1:
             frappe.throw("""At least one of the following must be selected:
                         <br>
                         <ul>
                            <li><b> Shift Start</b></li> 
                            <li><b> End Shift</b></li>
                            <li><b> In Shift </b></li> 
                        </ul>""" , title=_("Missing Leave Shift Type"))
        if self.leave_duration and self.leave_duration > 0 :
            shift_time_sql = frappe.db.sql("""
                            SELECT 
                                tst.start_time , tst.end_time
                            FROM `tabShift Type` tst 
                            INNER JOIN `tabShift Assignment` tsa ON tsa.shift_type = tst.name
            WHERE tsa.name = %s""" , (self.shift_assignment) , as_dict=True)
            shift_end_time = shift_time_sql[0]['end_time']
            shift_start_time = shift_time_sql[0]['start_time']
            time_format = "%H:%M:%S"
            if self.to_time and self.from_time:
                from_time = datetime.strptime(str(self.from_time), time_format)
                to_time = datetime.strptime(str(self.to_time), time_format)
                shift_start_time = datetime.strptime(str(shift_start_time), time_format)
                shift_end_time = datetime.strptime(str(shift_end_time), time_format)
                if self.leave_approver is None : 
                    frappe.throw(
                        """No leave approver has been assigned for this Employee : {employee}.<br> 
                        Please assign a Leave Approver Before Proceeding.""".format(employee=self.employee),
                        title=_("Leave Approver Required")
                    )
            if self.to_time:
                if to_time > shift_end_time:
                    frappe.throw(
                    """The End Time of your Leave Cannot be Later than the Shift End Time.
                    <br> Please adjust the End Time to be Within the Shift Period.""" , title=_("Leave Time Error"))
                
                if from_time < shift_start_time:
                    frappe.throw(
                    """The Start Time of your Leave Cannot be Earlier than the Shift Start Time.<br> 
                    Please adjust the Start time to be within the Shift Period.""" , title=_("Leave Time Error"))
        else:
            frappe.throw("Leave duration cannot be zero. Please enter a valid leave duration." , title=_("Missing Leave Duration"))
                