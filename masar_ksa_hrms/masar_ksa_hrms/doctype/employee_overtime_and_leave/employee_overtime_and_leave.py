# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.attendance_process.attendance_process import AttendanceProcess
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import period_validate , date_period 
from frappe.utils import get_link_to_form
class EmployeeOvertimeandLeave(Document):
	@frappe.whitelist()
	def get_date_period(self):
		return date_period(self)
	def validate(self):
		self.validation()
		self.get_leaves_salary_and_leaves_hour_rate()
		self.get_hours_rate_and_salaries()
		self.calculate_leaves_rate()
	def get_hours_rate_and_salaries(self):
		return AttendanceProcess.get_hours_rate_and_salaries(self)
	def get_number_of_days(self):
		return AttendanceProcess.get_number_of_days(self)
	def get_basic_salary_and_basic_salry_with_allowance(self):
		return AttendanceProcess.get_basic_salary_and_basic_salry_with_allowance(self)
	def calculate_leaves_salary(self):
		return AttendanceProcess.calculate_leaves_salary(self)
	def calculate_leaves_rate(self):
		return AttendanceProcess.calculate_leaves_rate(self)
	def get_leaves_salary_and_leaves_hour_rate(self):
		dict_ = AttendanceProcess.get_leaves_salary_and_leaves_hour_rate(self)
		self.leaves_salary = dict_.leaves_salary
		self.leaves_hour_rate = dict_.leaves_hour_rate
		return dict_
	@frappe.whitelist()
	def overtime_amount_calculations(self):
		self.get_leaves_salary_and_leaves_hour_rate()
		AttendanceProcess.calculate_overtime_rate(self)
		return 1
	def calculate_employee_overtime(self):
		overtime = frappe._dict({
							'ot_normal_day' : self.overtime_nd if self.overtime_nd else 0  , 
							'ot_off_day' :self.overtime_od if self.overtime_od else 0 , 
							'ot_holiday' : self.overtime_hd if self.overtime_hd else 0 
						})
		return overtime 
	def validation(self):
		data = period_validate(self)
		if data and data[0] and data[0][0]:
			frappe.throw(
    			'''Employee :<b>{emp}</b> Has Overtime and Leave Recorded Within the Same Period in Document <b>{docname}</b>. 
				<br> <br> To save this Document, 
				Please Ensure that the Employee Does Not Have Any Submitted Documents Overlapping with this period.
				'''.format(emp=get_link_to_form('Employee',self.employee ), docname = (get_link_to_form(self.doctype , data[0][0])))
			)
	def on_submit(self):
		self.additional_salary_for_overtime()
		self.additional_salary_for_leaves()
	
	def additional_salary_for_overtime(self):
		return AttendanceProcess.additional_salary_for_overtime(self)
	def additional_salary_for_leaves(self):
		return AttendanceProcess.additional_salary_for_leaves(self)
	