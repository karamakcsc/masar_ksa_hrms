# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from datetime import timedelta, datetime
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import date_period

class AttendanceProcessBulk(Document):
	
	def validate(self):
		self.update_employee_no()

	def on_submit(self):
		self.create_attendance_process()
	
	@frappe.whitelist()
	def get_date_period(self):
		return date_period(self)
	def update_employee_no(self):
		self.employees_no = int(len(self.employees))
	@frappe.whitelist()
	def get_employees(self):
		self.employees =[]
		cond = " 1=1"
		if self.department:
			cond += " AND te.department = '{department}'".format(department=self.department)
		if self.nationality:
			cond += " AND te.custom_nationality = '{nationality}'".format(nationality=self.nationality)
		if self.default_shift:
			cond  += f" AND te.default_shift = '{self.default_shift}'" 
   
		employees = frappe.db.sql(f"SELECT name , employee_name , department , custom_nationality , default_shift FROM `tabEmployee` te WHERE {cond}" , as_dict=True)	
		for employee in employees:
			self.append('employees',{
				'employee' :employee.name,
				'employee_name' : employee.employee_name,
				'department' : employee.department,
				'nationality': employee.custom_nationality,
				'default_shift':employee.default_shift
			})
		self.employees_no = int(len(employees))
		return True
	def create_attendance_process(self):
		posting_date=str(self.posting_date)
		without_shift=[]
		
		for emp in self.employees:
			
				
			if emp.default_shift:
				att_pro=frappe.new_doc('Attendance Process')
				att_pro.employee = emp.employee
				att_pro.employee_name = emp.employee_name
				att_pro.department=emp.department
				att_pro.posting_date=posting_date
				att_pro.company=self.company
				att_pro.bulk_reference=self
				att_pro.insert()
			else:
				without_shift.append(emp.employee)
		msg = ''
		if len(without_shift) != 0 :
			msg +=" Bulk Not Inserted For Employees Without Shift, are: <br> <ul>"
			for shift in without_shift:
				msg+= f'<li> Employee : <b> {shift} </b></il>'
			msg += '</ul>'
		if msg:
			frappe.msgprint(msg)
		
   
   
	@frappe.whitelist()	
	def submit_all_attendance_processes(self):
		attendance_processes = frappe.db.sql("SELECT name FROM `tabAttendance Process` WHERE bulk_reference = %s" , (self.name) , as_dict = True )
		without_ssa = list()
		
		for ap in attendance_processes:
			doc = frappe.get_doc('Attendance Process', ap.name)
			ssa_sql = frappe.db.sql("""SELECT name FROM `tabSalary Structure Assignment` tssa WHERE tssa.employee = %s  
                           AND tssa.from_date < %s AND tssa.docstatus = 1""" , (doc.employee , self.from_date  ) , as_dict= True)
			if not (ssa_sql and ssa_sql[0] and ssa_sql[0]['name']):
				without_ssa.append(doc.employee)
			else:
				doc.run_method("submit")
		msg2=''
		if len(without_ssa) != 0 :
			msg2+=" Bulk Not Submitted For Employees Without Salary Structure Assignment, are: <br> <ul>"
			for ssa in without_ssa:
				msg2+=f'<li> Employee: <b> {ssa} </b> </li>'
			msg2+='</ul>'
		if msg2:	
			frappe.msgprint(msg2)