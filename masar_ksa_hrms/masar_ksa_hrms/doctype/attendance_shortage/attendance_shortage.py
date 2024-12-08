# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt
import frappe
from frappe import _
import datetime
from datetime import timedelta , datetime
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import period_validate , date_period
class AttendanceShortage(Document):
    def validate(self):
        self.get_date_period()
        
    def on_submit(self):
        self.check_employee_in_period()
        self.create_short_leave_application()
        
        
    def holiday_date_in_period(self , shift_name , start_date , end_date ):
        try:
            if shift_name and start_date and end_date:
                holiday_dict = frappe.db.sql("""SELECT holiday_date 
					FROM tabHoliday th 
					WHERE parent = %s AND th.holiday_date BETWEEN %s AND %s
					ORDER BY idx""" , (shift_name , start_date , end_date) , as_dict=True)
                return holiday_dict
            else:
                return None
        except Exception as ex:
            frappe.throw(f'Error While Execute Holiday Date in Period: {str(ex)}')
            
    @frappe.whitelist()
    def get_date_period(self):
       return date_period(self)
   
    @frappe.whitelist()     
    def get_shortage_attendance(self):
        if not self.employee:
            frappe.throw("Set Employee", title=_("Missing Employee"))
            return
        if not self.posting_date:
            frappe.throw("Set Posting Date", title=_("Missing Posting Date"))
            return
        if self.from_date and self.to_date:
            from_date = self.from_date
            to_date = self.to_date
        else:
            date = self.get_date_period()
            if date:
                from_date = date.from_date
                to_date = date.to_date
            else:
                frappe.throw("Error in Period Date Please Add Posting Date", title=_("Error Period Date"))
                return
            
        employee_doc = frappe.get_doc('Employee', self.employee)
        if not employee_doc.default_shift:
            frappe.throw("Employee does not have a default shift assigned", title=_("Missing Default Shift"))
            return
        default_shift_name = employee_doc.default_shift
        holiday_dict = self.holiday_date_in_period(default_shift_name, from_date, to_date)
        holiday_dates = [holiday.holiday_date for holiday in holiday_dict]
        without_shift = []
        attendance_sql = frappe.db.sql("""
			SELECT
				name,
				shift,
				status,
				attendance_date,
				in_time,
				out_time,
				late_entry,
				early_exit
			FROM
				tabAttendance ta
			WHERE
				docstatus = 1
				AND employee = %s
				AND attendance_date BETWEEN %s AND %s;
		""", (self.employee, from_date, to_date), as_dict=True)
        total_duration = 0 
        if attendance_sql:
            self.attendance = []
            for att in attendance_sql:
                attendance_date = att.attendance_date
                if att.attendance_date in holiday_dates:
                    continue
                if att.shift:
                    shift_sql = frappe.db.sql("""
						SELECT start_time, end_time
						FROM `tabShift Type`
						WHERE name = %s
					""", (att.shift), as_dict=True)
                    if shift_sql:
                        start_time = (shift_sql[0]['start_time']).total_seconds()
                        end_time = (shift_sql[0]['end_time']).total_seconds()
                        start_of_day = datetime.combine(attendance_date, datetime.min.time())
                        row = frappe._dict({
                                'attendance': att.name ,
                                'attendance_date' : attendance_date , 
                                'shift_type' : att.shift, 
                                'status': att.status , 
                                'has_short_leave_application' : 0 , 
                                'action_type' : 'None Deduction' , 
                                'late_entry' : att.late_entry , 
                                'early_exit' : att.early_exit
                            })
                        if att.in_time or  att.out_time:
                            if att.in_time :
                                row['in_time'] =  att.in_time 
                                in_time_seconds = (att.in_time - start_of_day).total_seconds()
                                if int(att.late_entry) == 1:
                                    entry_duration = (in_time_seconds - start_time)
                                    total_duration+= entry_duration
                                    row['entry_duration'] = entry_duration
                            
                            if att.out_time:
                                row['out_time'] =  att.out_time 
                                out_time_seconds = (att.out_time - start_of_day).total_seconds()
                                if int(att.early_exit) ==1:
                                    exit_duration = (end_time - out_time_seconds)
                                    total_duration += exit_duration
                                    row['exit_duration'] = exit_duration
                        self.append('attendance' , row)  
                else:
                    without_shift.append(att.name)
            self.total_duration = total_duration
            if without_shift:
                msg = 'Attendance Without Shift are: <br><ul>'
                for without in without_shift:
                    msg += f'<li><b>Attendance</b> : {str(without)}</li>'
                msg += '</ul>'
                frappe.msgprint(msg, title=_("Attendance Without Shift"), indicator='red')
        else:
            frappe.msgprint(f"Employee {self.employee} has no Attendance in this Period", alert=True, indicator='red')
    
    def create_short_leave_application(self):
            hr_settings_doc = frappe.get_doc('HR Settings')
            standard_working_hours = float(hr_settings_doc.standard_working_hours)
            if standard_working_hours not in [0 , None]:
                hours = int(standard_working_hours)
                minutes = int((standard_working_hours - hours) * 60)
                swh_in_seconds = hours * 3600 + minutes * 60
                shift_assignment_doc = frappe.get_doc('Shift Assignment' , self.shift_assignment)
                shift_type_doc = frappe.get_doc('Shift Type' , shift_assignment_doc.shift_type)
                shift_sql = frappe.db.sql("""
						SELECT start_time, end_time
						FROM `tabShift Type`
						WHERE name = %s
					""", (shift_type_doc.name), as_dict=True)
                start_time = (shift_sql[0]['start_time'])
                end_time = (shift_sql[0]['end_time'])
                current_date = datetime.strptime(str(self.to_date), '%Y-%m-%d')
                if self.is_bulk == 1:
                    total_duration = self.total_duration
                    while total_duration > 0:
                        leave_duration = min(total_duration, swh_in_seconds)
                        dict_ = {
                            "attendance_shortage": self.name , 
                            "employee": self.employee,
                            "employee_name": self.employee_name,
                            "department": self.department,
                            "leave_approver": self.leave_approver,
                            "posting_date": self.to_date,
                            "company": self.company, 
                            "shift_assignment": self.shift_assignment,
                            "leave_type": self.leave_type,
                            "leave_date": current_date,
                            "in_shift": 1,
                            "from_time": start_time,
                            "leave_duration": leave_duration,
                            "to_time" : timedelta(seconds=float(start_time.total_seconds() + leave_duration))  , 
                            "status": "Approved",
                            "doctype": "Short Leave Application",
                        }
                        if self.action_type == 'Salary Deduction':
                            dict_["salary_deduction"] = 1
                            dict_["salary_component"] = self.salary_component
                        elif self.action_type == 'Balance Deduction':
                            dict_["balance_deduction"] = 1
                        else:
                            dict_["none_deduction"] = 1
                        new_sla = frappe.get_doc(dict_)
                        new_sla.insert(ignore_permissions=True) 
                        new_sla.run_method('submit')  
                        total_duration -= leave_duration
                        current_date -= timedelta(days=1)

                elif self.is_bulk == 0 :
                    if len(self.attendance) != 0 :
                        salary_components_durations = {}
                        balance_durations = {}
                        none_deduction = 0 
                        for att in self.attendance:
                            if att.has_short_leave_application == 0 :
                                duration = 0 
                                exit_duration = att.exit_duration if att.exit_duration else 0 
                                entry_duration = att.entry_duration if att.entry_duration else 0 
                                if exit_duration > 0:
                                        duration +=  exit_duration
                                if entry_duration > 0:
                                    duration +=  entry_duration
                                if duration > 0 :
                                    if att.action_type == 'Salary Deduction':
                                        salary_component = att.salary_component
                                        leave_type = att.leave_type   
                                        if salary_component not in salary_components_durations:
                                            salary_components_durations[salary_component] = {}
                                        if leave_type not in salary_components_durations[salary_component]:
                                            salary_components_durations[salary_component][leave_type] = 0
                                        salary_components_durations[salary_component][leave_type] += duration        
                                    elif att.action_type == 'Balance Deduction':
                                        if att.leave_type in balance_durations:
                                            balance_durations[att.leave_type] += duration
                                        else:
                                            balance_durations[att.leave_type] = duration
                                    elif att.action_type == 'None Deduction':
                                            none_deduction +=  duration

                    if salary_components_durations != {}:
                        for salary_comp_k ,  salary_comp_v in salary_components_durations.items():
                            salary_component = salary_comp_k
                            leaves = salary_comp_v
                            for leave_type , duration in leaves.items():
                                
                                while duration > 0:
                                    leave_duration = min(duration, swh_in_seconds)
                                    dict_ = {
                                        "attendance_shortage": self.name , 
                                        "employee": self.employee,
                                        "employee_name": self.employee_name,
                                        "department": self.department,
                                        "leave_approver": self.leave_approver,
                                        "posting_date": self.to_date,
                                        "company": self.company, 
                                        "shift_assignment": self.shift_assignment,
                                        "leave_type": leave_type,
                                        "leave_date": current_date,
                                        "in_shift": 1,
                                        "from_time": start_time,
                                        "salary_deduction" : 1 ,
                                        "leave_duration": leave_duration,
                                        "salary_component":salary_component , 
                                        "to_time" : timedelta(seconds=float(start_time.total_seconds() + leave_duration))  , 
                                        "status": "Approved",
                                        "doctype": "Short Leave Application",
                                    }
                                    new_sla = frappe.get_doc(dict_)
                                    new_sla.insert(ignore_permissions=True) 
                                    new_sla.run_method('submit')  
                                    duration -= leave_duration
                                    current_date -= timedelta(days=1)
                    if balance_durations != {}:
                        for leave , duration  in balance_durations.items():
                            while duration > 0:
                                    leave_duration = min(duration, swh_in_seconds)
                                    dict_ = {
                                        "attendance_shortage": self.name , 
                                        "employee": self.employee,
                                        "employee_name": self.employee_name,
                                        "department": self.department,
                                        "leave_approver": self.leave_approver,
                                        "posting_date": self.to_date,
                                        "company": self.company, 
                                        "shift_assignment": self.shift_assignment,
                                        "leave_type": leave,
                                        "leave_date": current_date,
                                        "in_shift": 1,
                                        "from_time": start_time,
                                        "balance_deduction" : 1 ,
                                        "leave_duration": leave_duration,
                                        "salary_component":salary_component , 
                                        "to_time" : timedelta(seconds=float(start_time.total_seconds() + leave_duration))  , 
                                        "status": "Approved",
                                        "doctype": "Short Leave Application",
                                    }
                                    new_sla = frappe.get_doc(dict_)
                                    new_sla.insert(ignore_permissions=True) 
                                    new_sla.run_method('submit')  
                                    duration -= leave_duration
                                    current_date -= timedelta(days=1)
                    if none_deduction != 0 :
                        frappe.msgprint(f"There is no Deduction time Duration : <b>{str(timedelta(seconds=none_deduction))}</b> . ")
            else:             
                frappe.throw("""Standard Working Hours have not been defined in the HR Settings. Please enter the required working hours to proceed.""" , title=_("Standard Working Hours"))

    def check_employee_in_period(self):
        data = period_validate(self)
        if len(data) != 0 :
            frappe.throw("This employee already has an attendance shortage record within the specified period.")

@frappe.whitelist()
def get_date_period_list(posting_date):
        try:
            if posting_date:
                posting_date = datetime.strptime(str(posting_date), '%Y-%m-%d').date()
                start_month = posting_date.replace(day=1)
                next_month = start_month.replace(day=28) + timedelta(days=4) 
                end_month = next_month - timedelta(days=next_month.day)
                return {
				'from_date': start_month, 
				'to_date' : end_month
				} 
            else : 
                return {
				'from_date': None, 
				'to_date' : None
				} 
        except Exception as ex:
            frappe.throw(f'Error While Execute Get Date Period: {str(ex)}')
            
@frappe.whitelist()
def get_employees(
        date_from, 
        date_to, 
        posting_date, 
        department=None, 
        nationality=None, 
        default_shift=None
    ):
    try:
        from masar_ksa_hrms.masar_ksa_hrms.doctype.attendance_shortage.attendance_shortage import AttendanceShortage as ATT
        get_shortage_attendance = ATT.get_shortage_attendance
        date_from = datetime.strptime(str(date_from) , "%Y-%m-%d")
        formatted_date = date_from.strftime("%Y-%m-%d")
        if department:
            conditions += f" AND te.department ='{department}'"
        if nationality: 
            conditions += f" AND te.custom_nationality ='{nationality}'"
        if default_shift: 
            conditions += f" AND te.default_shift ='{default_shift}'"
        conditions = "WHERE %s BETWEEN tsa.start_date AND tsa.end_date"
        data = """
            SELECT te.name, te.employee_name, te.department, te.default_shift, tsa.name AS shift_assignment
            FROM `tabEmployee` te
            LEFT JOIN `tabShift Assignment` tsa 
                ON tsa.employee = te.name 
                AND tsa.docstatus = 1 
                AND tsa.status = 'Active'
            {}
            ORDER BY te.name 
        """.format(conditions)
        without_sh_ass = list()
        without_default_shift = list()
        exist_employee = list()
        employees = frappe.db.sql(data, (formatted_date), as_dict=True)
        for emp in employees:
            if emp.shift_assignment:
                if emp.default_shift:
                    data_exist = frappe.db.sql("""SELECT 
                                                    name 
                                                FROM 
                                                    `tabAttendance Shortage` 
                                                WHERE 
                                                    employee = %s AND
                                                    docstatus = 1 AND
                                                    posting_date BETWEEN %s AND %s
                    """, (emp.name , date_from , date_to) , as_dict = True)
                    
                    if  len(data_exist) == 0 :
                        doc_dict =  {
                            'employee': emp.name,
                            'employee_name': emp.employee_name,
                            'department': emp.department,
                            'shift_assignment': emp.shift_assignment,
                            'posting_date': str(posting_date),
                            'is_bulk': 1
                            }
                        emp_doc = frappe.new_doc('Attendance Shortage').update(doc_dict).save()
                        get_shortage_attendance(emp_doc)
                        emp_doc.save()
                    else:
                      exist_employee.append(emp.name)       
                else: 
                  without_default_shift.append(emp)  
            else:
                without_sh_ass.append(emp)
        msg =''
        if len(without_sh_ass) != 0 :
            msg = 'The Below Employees Have no Shift Assignment Active and Submited:<br> <ul>'
            for sh_ass in without_sh_ass:
                msg += f'<li>Employee : <b>{sh_ass.name}</b></li>'
            msg+= '</ul>'
        if  len(without_default_shift) != 0:
            if msg in [None , '' , ' ' , 0 ]:
                msg =''
            else:
                msg += '<br>' 
            msg+= 'The Below Employees Have no Defualt Shift:<br><ul>'
            for default_shift in without_default_shift:
                msg+= f'<li>Employee : <b>{default_shift.name}</b></li>'
            msg+= '</ul>'
        if len (exist_employee) != 0:
            if msg in [None , '' , ' ' , 0 ]:
                msg =''
            else:
                msg += '<br>'
            msg+= 'The Below Employees aleady Have Attendance Shortage in the Same Period:<br><ul>'
            for ex_emp in exist_employee:
                msg+= f'<li>Employee : <b>{ex_emp}</b></li>'
            msg+= '</ul>'
        if msg not in [None , ' ' , '' , 0 ]:
            frappe.msgprint(str(msg) , title=_("Missing Standard Data") , indicator='red') 
    except Exception as ex:
        frappe.throw(f'Error while fetching employees: {str(ex)}')