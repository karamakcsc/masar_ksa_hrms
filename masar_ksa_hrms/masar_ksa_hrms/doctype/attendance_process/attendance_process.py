# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from datetime import timedelta, datetime
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import date_period , create_additional_salary
from frappe.utils import get_link_to_form
class AttendanceProcess(Document):
	def on_submit(self):
		self.set_linked_attendance()
		self.additional_salary_for_overtime()
		self.additional_salary_for_leaves()

	def validate(self):
		self.calculate_overtime_rate()
		self.calculate_leaves_rate()
	def on_trash(self):
		self.trash_linked_document()

	def holiday_date_in_period(self , shift_name , start_date , end_date ):
		try:
			if shift_name and start_date and end_date:
				h = frappe.qb.DocType('Holiday')
				holiday_dict = (
					frappe.qb.from_(h)
					.select(
						(h.holiday_date), 
						(h.weekly_off )
						)
					.where(h.parent == shift_name)
					.where(h.holiday_date.between(start_date , end_date))
					.orderby(h.idx)
				).run(as_dict = True)
				return holiday_dict
			else:
				return None
		except Exception as ex:
			frappe.throw(f'Error While Execute Holiday Date in Period: {str(ex)}')
   
   
	@frappe.whitelist()
	def get_date_period(self):
		return date_period(self)

	@frappe.whitelist()
	def get_number_of_days(self):
		try:
			if self.posting_date:
				if self.posting_date and (self.from_date is None or self.to_date is None):
					date = self.get_date_period()
					if date:
						self.from_date = date['from_date']
						self.to_date = date['to_date']
				if self.employee:
					payroll_settings = frappe.get_doc('Payroll Settings')
					employee_doc = frappe.get_doc('Employee' , self.employee)
					company_doc = frappe.get_doc('Company' , self.company)
					working_day_30= company_doc.custom_working_day_30
					if working_day_30 == 1 :
						return 30
					if employee_doc.default_shift:
						default_shift_name = employee_doc.default_shift
						default_shift_doc = frappe.get_doc('Shift Type' , default_shift_name)
						if payroll_settings.include_holidays_in_total_working_days:
							date = self.get_date_period()
							if date:
								self.from_date = date['from_date']
								self.to_date = date['to_date']
								from_date_obj = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
								to_date_obj = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
								number_of_days_full_period = (to_date_obj - from_date_obj).days + 1
								return number_of_days_full_period
						elif payroll_settings.include_holidays_in_total_working_days == 0 :
							if default_shift_doc.holiday_list:
								date = self.get_date_period()
								if date:
									self.from_date = date['from_date']
									self.to_date = date['to_date']
									from_date_obj = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
									to_date_obj = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
									number_of_days_full_period = (to_date_obj - from_date_obj).days + 1
								if number_of_days_full_period and default_shift_name and self.from_date and self.to_date:
									hoilday_list = self.holiday_date_in_period(default_shift_name , self.from_date ,  self.to_date )
									if len(hoilday_list) != 0:
										number_of_days = number_of_days_full_period - len(hoilday_list)
									else:
										number_of_days = number_of_days_full_period
									return number_of_days
								else:
									frappe.throw(
             								"Missing Shift and Date for Holiday List" , 
                     						title=_("Missing Hoilday Data")
                        			)
							else:
								frappe.throw(
            								f"Set Holiday List is Shift Type {default_shift_name}" , 
                							title=_("Missing Holiday List")
                       				)	
					else:
						frappe.throw(
          							f"Set Employee Default Shift for Employee: {self.employee}" , 
                 					title=_("Missing Employee Default Shift")
                      	)
				else:
					frappe.throw(
         					"Set Employee" , 
              				title=_("Missing Employee")
                  		)
			else:
				frappe.throw(
        			"Set Posting Date" , 
           			title=_("Missing Posting Date")
              	)
		except Exception as ex:
			frappe.throw(
       			f'Error While Execute Get Number of Days: {str(ex)}'
          	)
	
	@frappe.whitelist()
	def get_basic_salary_and_basic_salry_with_allowance(self):
		try:
			basic_salary = 0 
			basic_salary_with_allowance = 0 
			if self.employee and self.posting_date:
				if self.posting_date and (self.from_date is None or self.to_date is None):
					date = self.get_date_period()
					if date:
						self.from_date = date['from_date']
						self.to_date = date['to_date']
				from_date = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
				to_date = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
				employee_doc = frappe.get_doc('Employee' , self.employee )
				if self.department:
					department_doc = frappe.get_doc('Department' , self.department)
					basic_sc = department_doc.custom_salary_component
					company_doc = frappe.get_doc('Company' , self.company)
					if basic_sc is None:
						basic_sc = company_doc.custom_salary_component
				if basic_sc in [None , '' , ' ']:
					frappe.throw(f"Set Default Basic Salary in Company {str(self.comany)} in Salary Component.or in Department:{self.department}" , 
                  	title=_("Missing Default Basic Salary")
                   	)
				for esc in employee_doc.custom_employee_salary_component:
					if esc.salary_component == basic_sc:
						basic_salary = esc.esc_amount
					if esc.is_active and (from_date <= datetime.strptime(str(esc.date), '%Y-%m-%d').date() <= to_date):
						if esc.salary_component != basic_sc:
							sal_comp_doc = frappe.get_doc('Salary Component' , esc.salary_component)
							if sal_comp_doc.custom_is_overtime_applicable:
								basic_salary_with_allowance += esc.esc_amount
				basic_salary_with_allowance = basic_salary_with_allowance + basic_salary
				return frappe._dict({
						'basic_salary' : basic_salary,
						'basic_salary_with_allowance' : basic_salary_with_allowance
					})
			else:
				frappe.throw(
        			f"Set Employee and Posting Date" , 
           			title=_("Missing Standard Fields")
              	)
		except Exception as ex:
			frappe.throw(
       			f'Error While Execute Get Basic Salary and Basic Salary With Allowance:{str(ex)}'
          	)
	def get_salary_component(self):
		ot = frappe.qb.DocType('Overtime Type')
		sc = (
			frappe.qb.from_(ot)
			.select(ot.name)
		)
		if self.department:
			department_sc = sc.where(ot.department == self.department).run(as_dict = True)
		if len(department_sc) != 3:
			company_sc = sc.where(ot.is_general == 1).run(as_dict = True)
			if len(company_sc) !=3:
				frappe.throw(
					f"""Check Overtime Type must have three types (Normal Day , Off Day , Holidays) 
					For Department: {self.department} or three types as General."""
				)
			else:
				sc = sc.where(ot.is_general == 1)
		else:
			sc = sc.where(ot.department == self.department)
		
		sc_nd = sc.where(ot.normal_day == 1).run(as_dict = True)				
		if sc_nd and sc_nd[0] and sc_nd[0]['name']:
			self.overtime_type_nd = sc_nd[0]['name']
		else: 
			frappe.throw(
					'Set Overtime Type where Type is Normal Day for Department {dep}'
     				.format(dep = self.department), 
					title=_('Missing Normal Day Overtime Type')
			)
		sc_od = sc.where(ot.off_day == 1).run(as_dict = True)
		if sc_od and sc_od[0] and sc_od[0]['name']:
			self.overtime_type_od = sc_od[0]['name']
		else: 
			frappe.throw(
					'Set Overtime Type where Type is Off Day for Department {dep}'
					.format(dep = self.department),
					title=_('Missing Off Day Overtime Type')
			)
		
		sc_hd = sc.where(ot.holidays == 1).run(as_dict = True)
		if sc_hd and sc_hd[0] and sc_hd[0]['name']:
			self.overtime_type_hd = sc_hd[0]['name']
		else: 
			frappe.throw(
					'Set Overtime Type where Type is Holidays for Department {dep}'
     				.format(dep = self.department),
					title=_('Missing Holidays Overtime Type')
			)
		return 1 
	@frappe.whitelist()
	def get_hours_rate_and_salaries(self):
		try:
			number_of_payment_days = self.get_number_of_days()
			salaries = self.get_basic_salary_and_basic_salry_with_allowance()
			if self.employee:
				employee_doc = frappe.get_doc('Employee' , self.employee)
				if employee_doc.default_shift:
					shift_type_doc = frappe.get_doc('Shift Type' ,  employee_doc.default_shift)
					start_time = shift_type_doc.start_time
					end_time = shift_type_doc.end_time
					time_duration_str = str(end_time - start_time)
					time_format = '%H:%M:%S'
					time_duration = datetime.strptime(time_duration_str, time_format)
					hours = time_duration.hour
					minutes = time_duration.minute
					number_of_hours = hours + minutes / 60
					basic_salary = salaries.basic_salary
					basic_salary_with_allowance = salaries.basic_salary_with_allowance
					basic_salary_in_hour = basic_salary / number_of_hours
					basic_salary_with_allowance_in_hour = basic_salary_with_allowance / number_of_hours
					bs_hour_rate = round(float(basic_salary_in_hour) / float(number_of_payment_days) , 3)
					bswa_hour_rate = round(float(basic_salary_with_allowance_in_hour) / float(number_of_payment_days) , 3)
					self.working_day = int(number_of_payment_days)
					self.basic_salary = basic_salary
					self.basic_salary_with_allowances = basic_salary_with_allowance
					self.bs_hour_rate = bs_hour_rate
					self.bswa_hour_rate = bswa_hour_rate
					dict_ =  frappe._dict(
         				{
						'working_day' : number_of_payment_days,
						'basic_salary' : basic_salary, 
						'basic_salary_with_allowance': basic_salary_with_allowance,
						'basic_salary_hour_rate' : bs_hour_rate,
						'basic_salary_with_allowance_hour_rate': bswa_hour_rate
						}
             		)
					return dict_
				else:
					frappe.throw(
         				f"Self Employee Default Shift for Employee: {self.employee}" , 
             			title=_("Missing Employee Default Shift")
                	)
			else:
				frappe.throw(
        			"Set Employee" , 
           			title=_("Missing Employee")
              	)
		except Exception as ex:
			frappe.throw(
       			f'Error While Execute Get Hours rate and Salaies: {str(ex)}'
          	)

	def calculate_employee_overtime(self):
		try:
			def get_weekly_off(
					holiday_lst, 
					date , 
					h = frappe.qb.DocType('Holiday')
			):
					return (
					frappe.qb.from_(h)
					.select(h.weekly_off)
					.where(h.parent == holiday_lst)
					.where(h.holiday_date == date)
				).run(as_dict = True)
			self.overtime_details=[]
			over_time_nd_in_seconds = 0
			over_time_fd_in_seconds = 0 
			over_time_hd_in_seconds = 0 
			if self.posting_date:
				if self.posting_date and (self.from_date is None or self.to_date is None):
					date = self.get_date_period()
					if date:
						self.from_date = date['from_date']
						self.to_date = date['to_date']
				if self.to_date and self.from_date and self.employee:
					emp_doc = frappe.get_doc("Employee" , self.employee)
					is_overtime_applicable = emp_doc.is_overtime_applicable
					if is_overtime_applicable == 0 :
						frappe.msgprint(
          					_("Employee: {0} is not Eligible for Overtime").format(get_link_to_form('Employee' , self.employee)), 
               				title=_("Overtime Not Applicable")
               				)
						return False 
					e = frappe.qb.DocType('Employee')
					a = frappe.qb.DocType('Attendance')
					st = frappe.qb.DocType('Shift Type')
					attendance_sql = ((
						frappe.qb.from_(a)
						.select(
							(a.name) , 
							(a.employee) , 
							(a.employee_name) , 
							(a.department), 
							(a.attendance_date), 
							(a.in_time) ,
							(a.out_time) ,
							(st.start_time) ,
							(st.end_time) ,
							(st.custom_enable_early_entry_marking) ,
							(st.custom_early_entry_grace_period) , 
							(st.custom_enable_late_exit_marking) ,
							(st.custom_late_exit_grace_period) ,
							(st.holiday_list)
						)
						.join(st)
						.on(st.name == a.shift)
						.join(e)
						.on(e.name == a.employee)
						.where(e.is_overtime_applicable  == 1)
						.where(a.status == 'Present')
						.where(a.employee == self.employee)
						.where(a.attendance_date.between(
							self.from_date , self.to_date 
						)
						)
					)
					.run(as_dict = True))
					print(attendance_sql)
					if len(attendance_sql) != 0 :
						for att in attendance_sql:
							employee = att.employee
							employee_name = att.employee_name
							department = att.department
							attendance_date = att.attendance_date
							in_time = att.in_time
							out_time = att.out_time
							start_time= att.start_time
							end_time = att.end_time
							enable_early_entry_marking =att.custom_enable_early_entry_marking
							early_entry_grace_period = att.custom_early_entry_grace_period
							enable_late_exit_marking = att.custom_enable_late_exit_marking
							late_exit_grace_period = att.custom_late_exit_grace_period
							holiday_list_att = att.holiday_list
							### Covert To Seconds
							start_seconds = start_time.total_seconds()
							end_seconds = end_time.total_seconds()
							start_of_day = datetime.combine(attendance_date, datetime.min.time())
							in_time_seconds = (in_time - start_of_day).total_seconds()
							out_time_seconds = (out_time - start_of_day).total_seconds()

							if enable_early_entry_marking:
								overtime_start_seconds = start_seconds - (early_entry_grace_period *60)
							else:
								overtime_start_seconds = start_seconds
							if enable_late_exit_marking:
								overtime_end_seconds = end_seconds + (late_exit_grace_period*60)
							else: 
								overtime_end_seconds = end_seconds
							holiday_list = list()
							holiday_date_sql = self.holiday_date_in_period( 
									shift_name = holiday_list_att , 
									start_date = self.from_date , 
									end_date = self.to_date 
							)
							att_date = datetime.strptime(str(attendance_date), '%Y-%m-%d').date()
							for holiday_date in holiday_date_sql:
								holiday_list.append(holiday_date.holiday_date)
							employee_overtime_before_shift_seconds = 0 
							employee_overtime_after_shift_seconds = 0 
							if att_date in holiday_list:
									weekly_off_sql = get_weekly_off(holiday_lst=holiday_list_att , date=att_date)
									if weekly_off_sql and weekly_off_sql[0] and weekly_off_sql[0]['weekly_off']:
										weekly_off = int(weekly_off_sql[0]['weekly_off'])
									if weekly_off == 1 :
									###### Calculate Overtime For OFF Day Time ######
										day_time_in_seconds = out_time_seconds - in_time_seconds
										over_time_fd_in_seconds += day_time_in_seconds
										self.append('overtime_details',{
											'attendance' : att.name , 
											"employee":employee,
											'employee_name': employee_name,
											'time_in':in_time,
											'time_out':out_time,
											"overtime":day_time_in_seconds ,
											"attendance_date":attendance_date,
											'off_day': 1
											})
									###### Calculate Overtime For Holidays Time ######
									elif weekly_off == 0:
										holiday_time_in_seconds = out_time_seconds - in_time_seconds
										over_time_hd_in_seconds += holiday_time_in_seconds
										self.append('overtime_details',{
											'attendance' : att.name , 
											"employee":employee,
											'employee_name': employee_name,
											'time_in':in_time,
											'time_out':out_time,
											"overtime":holiday_time_in_seconds ,
											"attendance_date":attendance_date,
											'holiday': 1
											})
							else: 
									###### Calculate Overtime For Normal Day Time ######
								if in_time_seconds < overtime_start_seconds:
									employee_overtime_before_shift_seconds = overtime_start_seconds - in_time_seconds
								if out_time_seconds > overtime_end_seconds:
									employee_overtime_after_shift_seconds = out_time_seconds - overtime_end_seconds
								if employee_overtime_after_shift_seconds + employee_overtime_before_shift_seconds > 0 :
									employee_overtime_in_day_seconds = employee_overtime_after_shift_seconds + employee_overtime_before_shift_seconds
								over_time_nd_in_seconds +=  employee_overtime_in_day_seconds
								self.append('overtime_details',{
											'attendance' : att.name , 
											"employee":employee,
											'employee_name': employee_name,
											'time_in':in_time,
											'time_out':out_time,
											"overtime":employee_overtime_in_day_seconds ,
											"attendance_date":attendance_date,
											'normal_day': 1
											})
						overtime = frappe._dict({
							'ot_normal_day' : over_time_nd_in_seconds , 
							'ot_off_day' :over_time_fd_in_seconds , 
							'ot_holiday' : over_time_hd_in_seconds
						})
						return overtime
				else: 
					frappe.throw(
         				f"Set Employee and Posting Date" , 
             			title=_("Missing Standard Fields")
                	)
			else:
				frappe.throw(
        			f"Set Employee and Posting Date" , 
           			title=_("Missing Standard Fields")
              	)
		except Exception as ex:
			frappe.throw(
       				f'Error While Execute Calculate Employee Overtime: {str(ex)}'
           )



	def calculate_overtime_rate(self):
		try:
			if self.doctype == 'Attendance Process':
				self.get_salary_component()
			amount_nd , amount_od , amount_hd  = 0 , 0 , 0 
			data_salary = self.get_hours_rate_and_salaries()
			working_day = data_salary.working_day
			basic_salary =  data_salary.basic_salary 
			basic_salary_with_allowance = data_salary.basic_salary_with_allowance
			basic_salary_hour_rate = data_salary.basic_salary_hour_rate
			basic_salary_with_allowance_hour_rate = data_salary.basic_salary_with_allowance_hour_rate
			overtime_data = self.calculate_employee_overtime()
			if overtime_data:
				normal_day_in_seconds = overtime_data.ot_normal_day
				off_day_in_seconds = overtime_data.ot_off_day
				holiday_in_seconds = overtime_data.ot_holiday
				if self.overtime_type_nd:
						self.overtime_nd = normal_day_in_seconds
						amount_basic_with_allowance_nd = float(basic_salary_with_allowance_hour_rate) * (normal_day_in_seconds/3600)
						amount_basic_nd = float(basic_salary_hour_rate) * (float(normal_day_in_seconds)/3600) * (float(self.overtime_rate_nd if self.overtime_rate_nd else 0 ) - 1 )
						amount_nd = amount_basic_with_allowance_nd + amount_basic_nd
				if self.overtime_type_od:
						self.overtime_od = off_day_in_seconds
						amount_basic_od = float(basic_salary_hour_rate) * (float(off_day_in_seconds)/3600) * (float(self.overtime_rate_od if self.overtime_rate_od else 0 ) - 1 )
						amount_basic_with_allowance_od =  float(basic_salary_with_allowance_hour_rate) * (off_day_in_seconds/3600)
						amount_od = amount_basic_with_allowance_od + amount_basic_od
				if self.overtime_type_hd:
						self.overtime_hd = holiday_in_seconds
						amount_basic_hd = float(basic_salary_hour_rate) * (float(holiday_in_seconds)/3600) * (float(self.overtime_rate_hd if self.overtime_rate_hd else 0 ) - 1 )
						amount_basic_with_allowance_hd =  float(basic_salary_with_allowance_hour_rate) * (holiday_in_seconds/3600)
						amount_hd = amount_basic_with_allowance_hd + amount_basic_hd
				self.amount_hd = amount_hd
				self.amount_nd = amount_nd
				self.amount_od = amount_od
				self.working_day = int(working_day)
				self.basic_salary = basic_salary
				self.basic_salary_with_allowances = basic_salary_with_allowance
				self.bs_hour_rate = basic_salary_hour_rate
				self.bswa_hour_rate = basic_salary_with_allowance_hour_rate
				self.total_nd = amount_nd
				self.total_hd = amount_hd
				self.total_od = amount_od
				self.ot_total_amount = float(amount_nd + amount_hd + amount_od)
		except Exception as ex:
			frappe.throw(f'Error While Execute Calculate Overtime Rate: {str(ex)}')
   
	@frappe.whitelist()
	def set_linked_attendance(self):
		try:
			if len(self.overtime_details) != 0:
				for overtime_details in self.overtime_details:
					overtime_details.attendance
					if overtime_details.attendance : 
						att_doc = frappe.get_doc('Attendance' , overtime_details.attendance)
						att_doc.custom_att_pro_ref = self.name
						att_doc.save()
			return 1 
		except Exception as ex:
			frappe.throw(
       				f'Error While Execute Set Linked Attendance: {str(ex)}'
           	)
				
	def additional_salary_for_overtime(self):
		try:
			if self.total_nd or self.total_od or self.total_hd:
				salary_components = {}
				if self.total_nd:
					if self.sc_overtime_nd in salary_components:
						salary_components[self.sc_overtime_nd] += float(self.total_nd)
					else:
						salary_components[self.sc_overtime_nd] = float(self.total_nd)	
				if self.total_hd:
					if self.sc_overtime_hd in salary_components:
						salary_components[self.sc_overtime_hd] += float(self.total_hd)
					else:
						salary_components[self.sc_overtime_hd] = float(self.total_hd)	
				if self.total_od:
					if self.sc_overtime_od in salary_components:
						salary_components[self.sc_overtime_od] += float(self.total_od)
					else:
						salary_components[self.sc_overtime_od] = float(self.total_od)
				for salary_component, total in salary_components.items():
						data = frappe._dict({
							'employee' :  self.employee, 
							'employee_name' : self.employee_name,
							'department' : self.department,
							'company' : self.company,
							'is_recurring' :  0,
							'payroll_date' : self.to_date,
							'salary_component' :  salary_component,
							'type' : "Deduction",
							'amount' :  total,
							'deduct_full_tax_on_selected_payroll_date' :  1,
							'overwrite_salary_structure_amount' :  1,
							'ref_doctype' : self.doctype,
							'ref_docname' : self.name
						})
						additional_salary = create_additional_salary(data)
						if salary_component == self.sc_overtime_nd and self.total_nd != 0 :
							self.add_sal_nd = additional_salary.name
						if salary_component == self.sc_overtime_od and self.total_od != 0 :
							self.add_sal_od = additional_salary.name
						if salary_component == self.sc_overtime_hd and self.total_hd != 0 :
							self.add_sal_hd = additional_salary.name
						frappe.msgprint(
							"The Additional Salary for Overtime has been Successfully Created.",
							alert=True ,
							indicator='green'
						)
			else:
				frappe.msgprint("No Additional Salary for Overtime Records Were Found." ,
					alert=True ,
					indicator='blue'
				)
		except Exception as ex:
			frappe.throw(f'Error While Execute Additional Salary For Overtime: {str(ex)}')

	@frappe.whitelist()
	def remove_linked_attendance_overtime(self):
		att_doc_sql = frappe.db.sql("SELECT name FROM `tabAttendance` WHERE custom_att_pro_ref = %s" , (self.name) , as_dict=True)
		if len(att_doc_sql) !=0:
			for att_doc in att_doc_sql:
				linked_att_doc = frappe.get_doc('Attendance' , att_doc.name)
				linked_att_doc.custom_att_pro_ref = None
				linked_att_doc.save()
		frappe.msgprint('Linked Attendance is Removed Successfully.' , alert=True)
		return 1 


				
	def trash_linked_document(self):
		#### Cannot Delete Additional Salary For Over Time 
			msg = ''
			add_sal_sql = frappe.db.sql(
       				"SELECT name FROM `tabAdditional Salary` WHERE ref_docname = %s" , 
           			(self.name) , 
              		as_dict=True
                )
			if len(add_sal_sql) !=0 :
				msg+= 'Cannot Delete Document Before Delete Linked Additional Salary: <br><ul>'
				for add_sal in add_sal_sql:
					link_add_sal = frappe.get_doc('Additional Salary' , add_sal.name)
					msg+= f'<li><b> Additional Salary </b> : {str(link_add_sal.name)}</li>'
			if msg not in [None , ' ' , '' ,""]:
				frappe.throw(msg , title=_('Delete Linked Document'))

	def calculate_leaves_salary(self):
		try:
			basic_salary = 0 
			leaves_salary = 0 
			leaves_salary_comp = 0 
			sc_basic = list()
			if self.employee and self.posting_date:
				if self.posting_date and (self.from_date is None or self.to_date is None):
					date = self.get_date_period()
					if date:
						self.from_date = date['from_date']
						self.to_date = date['to_date']
				from_date = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
				to_date = datetime.strptime(str(self.to_date), '%Y-%m-%d').date()
				employee_doc = frappe.get_doc('Employee' , self.employee )
				company_doc = frappe.get_doc('Company' , self.company)
				department_doc = frappe.get_doc('Department' , self.department)
				if company_doc.custom_salary_component:
					sc_basic.append(company_doc.custom_salary_component)
				if department_doc.custom_salary_component:
					sc_basic.append(department_doc.custom_salary_component)
				if len(sc_basic) == 0:
					frappe.throw(
         					f"Set Default Basic Salary in Company {str(self.comany)} in Salary Component or in Department :{str(self.department)}" ,
                  			title=_("Missing Default Basic Salary")
                    )
				basic_in_table = None
				for esc in employee_doc.custom_employee_salary_component:
					if esc.salary_component in sc_basic:
						basic_in_table = esc.salary_component
						basic_salary = esc.esc_amount
					if esc.is_active and (from_date <= datetime.strptime(str(esc.date), '%Y-%m-%d').date() <= to_date):
						if esc.salary_component != basic_in_table:
							sal_comp_doc = frappe.get_doc('Salary Component' ,esc.salary_component )
							if sal_comp_doc.custom_is_short_leave_applicable:
								leaves_salary_comp += esc.esc_amount
				leaves_salary = leaves_salary_comp + basic_salary
				return leaves_salary
			else:
				frappe.throw(
						f"Set Employee and Posting Date" , 
						title=_("Missing Standard Fields")
                )
		except Exception as ex:
			frappe.throw(f'Error While Execute Calculate Leaves Salary :{str(ex)}')
	


	def get_leaves_salary_and_leaves_hour_rate(self):
		try:
			leaves_salary = self.calculate_leaves_salary()
			number_of_payment_days = self.get_number_of_days()
			if self.employee:
					employee_doc = frappe.get_doc('Employee' , self.employee)
					if employee_doc.default_shift:
						shift_type_doc = frappe.get_doc('Shift Type' ,  employee_doc.default_shift)
						start_time = shift_type_doc.start_time
						end_time = shift_type_doc.end_time
						time_duration_str = str(end_time - start_time)
						time_format = '%H:%M:%S'
						time_duration = datetime.strptime(time_duration_str, time_format)
						hours = time_duration.hour
						minutes = time_duration.minute
						number_of_hours = hours + minutes / 60
						leaves_hour_rate = (float(leaves_salary) / float(number_of_hours)) / float(number_of_payment_days)
						leaves_dict = frappe._dict({
							'leaves_salary': leaves_salary , 
							'leaves_hour_rate' : leaves_hour_rate
						})
						return leaves_dict
					else:
						frappe.throw(f"Self Employee Default Shift for Employee: {self.employee}" ,
                   						title=_("Missing Employee Default Shift")
                        )
			else:
				frappe.throw("Set Employee" ,
                 			title=_("Missing Employee")
            	)
		except Exception as ex:
			frappe.throw(f'Error While Execute Get Hours rate and Salaies: {str(ex)}')

	def calculate_leaves_rate(self):
		leave = self.get_leaves_salary_and_leaves_hour_rate()
		leaves_salary = leave.leaves_salary
		leaves_hour_rate = leave.leaves_hour_rate
		if self.posting_date:
			if self.from_date and self.to_date:
				from_date = self.from_date 
				to_date = self.to_date
			else: 
				date = self.get_date_period()
				if date : 
					from_date = date.from_date
					to_date = date.to_date
			sla = frappe.qb.DocType('Short Leave Application')
			lt = frappe.qb.DocType('Leave Type')
			short_leave_application = (
					frappe.qb.from_(sla)
					.select(
						(sla.name),
						(sla.salary_component),
						(sla.leave_type),
						(sla.leave_date),
						(sla.from_time),
						(sla.leave_duration),
						(sla.to_time),
						(lt.custom_salary_deduction_rate)
					)
					.join(lt)
					.on(lt.name == sla.leave_type)
					.where(sla.docstatus == 1 )
					.where(sla.status == 'Approved')
					.where(sla.leave_date.between(
						from_date , to_date
					))
				)
			if self.doctype  == 'Employee Overtime and Leave':
				short_leave_application = short_leave_application.where(sla.salary_deduction == 1)
			short_leave_application_sql = short_leave_application.run(as_dict = True )
			total_amount = 0 
			self.leaves_table = []
			if len(short_leave_application_sql) != 0 :
				for sla in short_leave_application_sql:
					amount_row =  round(float(sla.custom_salary_deduction_rate) * float(leaves_hour_rate) * (sla.leave_duration /3600) , 3)
					total_amount+=amount_row
					self.append('leaves_table' , {
						'short_leave_application' : sla.name, 
						'salary_component' : sla.salary_component , 
						'leave_type' : sla.leave_type , 
						'leave_date' : sla.leave_date , 
						'from_time' : sla.from_time , 
						'leave_duration': sla.leave_duration , 
						'to_time': sla.to_time , 
						'salary_deduction_rate': sla.custom_salary_deduction_rate , 
						'leave_hour_rate': leaves_hour_rate , 
						'amount' : amount_row
					})
			else : 
				total_amount = 0 
			self.leaves_salary = leaves_salary
			self.leaves_hour_rate = leaves_hour_rate
			self.total_amount = total_amount


	def additional_salary_for_leaves(self):
		if self.total_amount:
			add_sal_leaves_sql = frappe.db.sql("""
					SELECT sum(amount) AS amount, salary_component
					FROM `tabAttendance Process Short Leaves Details`
					WHERE parent = %s
					GROUP BY salary_component
					""" , (self.name) , as_dict = True)
			if len (add_sal_leaves_sql) != 0 :
				for add_sal in add_sal_leaves_sql:
					data = frappe._dict({
					'employee' : self.employee , 
					'employee_name' : self.employee_name,
					'department' : self.department,
					'company' : self.company,
					'is_recurring' :  0,
					'payroll_date' : self.to_date,
					'salary_component' :  add_sal.salary_component,
					'type' : "Deduction",
					'amount' :  add_sal.amount,
					'deduct_full_tax_on_selected_payroll_date' :  1,
					'overwrite_salary_structure_amount' :  1,
					'ref_doctype' : self.doctype,
					'ref_docname' : self.name
					})
					create_additional_salary(data)
				frappe.msgprint(
							"The Additional Salary for Leaves has been Successfully Created.",
							alert=True ,
							indicator='green'
						)
		else:
				frappe.msgprint("No Additional Salary for Leaves Records Were Found." ,
					alert=True ,
					indicator='blue'
				)