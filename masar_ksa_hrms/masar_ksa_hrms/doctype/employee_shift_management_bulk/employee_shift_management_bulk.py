# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _
from frappe.model.document import Document


class EmployeeShiftManagementBulk(Document):
	def validate(self):
		self.update_employee_no()
	def on_submit(self):
		self.create_emp_shift_management()
	@frappe.whitelist()
	def get_employees(self):
		self.emp_table =[]
		cond = " 1=1"
		if self.department:
			cond += " AND te.department = '{department}'".format(department=self.department)
		if self.nationality:
			cond += " AND te.custom_nationality = '{nationality}'".format(nationality=self.nationality)
		employees = frappe.db.sql(f"SELECT name , employee_name , department , custom_nationality FROM `tabEmployee` te WHERE {cond}" , as_dict=True)
		for employee in employees:
			self.append('emp_table',{
				'employee' :employee.name,
				'employee_name' : employee.employee_name,
				'department' : employee.department,
				'nationality': employee.custom_nationality
			})
		self.employees_no = int(len(employees))
		return True
	def create_emp_shift_management(self):
		new_esm_list = list()
		frappe.msgprint(
				_("Employee Shift Management is queued. It may take a few minutes"),
				alert=True,
				indicator="blue",
			)
		employees = frappe.db.sql("""
			select 	tesmb.name , 
					tesmbd.employee ,
					tesmbd.employee_name ,
					tesmbd.department ,
					tesmbd.nationality 
			FROM `tabEmployee Shift Management Bulk` tesmb 
			INNER JOIN `tabEmployee Shift Management Bulk Details` tesmbd ON tesmb.name = tesmbd.parent 
			WHERE tesmb.name = %s
		""" , (self.name) , as_dict=True)
		exist_esm = list()
		for employee in employees:
			sql = frappe.db.sql("""
				SELECT name , employee
				FROM `tabEmployee Shift Management` tesm 
				WHERE docstatus =1  AND employee = %s AND %s BETWEEN tesm.start_date AND tesm.end_date ;
			""", (employee.employee , str(self.start_date)), as_dict=True)

			if sql and sql[0]:
					exist_esm.append(frappe._dict({'esm':sql[0]['name'] ,'emp' : sql[0]['employee'] }))
			else:
				new_esm = frappe.new_doc('Employee Shift Management')
				new_esm.employee = employee.employee
				new_esm.employee_name = employee.employee_name
				new_esm.department = employee.department
				new_esm.nationality = employee.nationality
				new_esm.status = self.status
				new_esm.posting_date = self.posting_date 
				new_esm.start_date = self.start_date 
				new_esm.end_date = self.end_date
				new_esm.saturday_st = self.saturday_st
				new_esm.sunday_st = self.sunday_st
				new_esm.monday_st = self.monday_st
				new_esm.tuesday_st = self.tuesday_st
				new_esm.wednesday_st = self.wednesday_st
				new_esm.thursday_st = self.thursday_st
				new_esm.friday_st = self.friday_st
				new_esm.reference_bulk = self.name
				new_esm.save(ignore_permissions=True)
				new_esm_list.append(new_esm.name)
			
			
		try:
			for esm in new_esm_list:	
				to_submit_esm = frappe.get_doc('Employee Shift Management' , esm)
				to_submit_esm.submit()

		
			frappe.msgprint(
					_("Employee Shift Management is Sucessfully Execute"),
					alert=True,
					indicator="green",
				)
			if len(exist_esm) != 0 :
				msg = 'The Following Employees have Employee Shift Management in the same period: <br> <ul>'
				for esm in exist_esm:
					msg +=f' <li>Employee : <b>{str(esm.emp)}</b> has Employee Shift Management:<b> {str(esm.esm)} </b></li>'
				msg+= '</ul>'

				frappe.msgprint(_(msg) , title="Exist Employee Shift Management")
		except Exception as ex : 
			frappe.throw('There is Exception while Submiting :'+str(ex))
		
	def update_employee_no(self):
		self.employees_no = int(len(self.emp_table))

