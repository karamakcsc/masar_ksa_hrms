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
		e = frappe.qb.DocType('Employee')
		employees = (
			frappe.qb.from_(e)
			.select(
				(e.name),
				(e.employee_name),
				(e.department),
				(e.custom_nationality)
			)
   			.where(e.status == 'Active')

		)
		if self.department:
			employees = employees.where(e.department == self.department)
		if self.nationality:
			employees = employees.where(e.custom_nationality == self.nationality)
		employees = employees.run(as_dict=True)
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
		esmbd = frappe.qb.DocType('Employee Shift Management Bulk Details')
		esmb = frappe.qb.DocType('Employee Shift Management Bulk')
		esm = frappe.qb.DocType('Employee Shift Management')
		employees = (
			frappe.qb.from_(esmb)
			.join(esmbd).on(esmb.name == esmbd.parent )
			.select(
				(esmbd.name),
				(esmbd.employee),
				(esmbd.employee_name),
				(esmbd.department),
				(esmbd.nationality)
			)
			.where(esmb.name == self.name)
		).run(as_dict = True)
		exist_esm = list()
		start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d")
		start_month = start_date.month
		start_year = start_date.year
		end_date = datetime.strptime(str(self.end_date), "%Y-%m-%d")
		end_month = end_date.month
		end_year = end_date.year
		for employee in employees:
			query ="""
					SELECT name, employee
					FROM `tabEmployee Shift Management` esm
					WHERE esm.docstatus = 1
					AND esm.employee = %s
					AND MONTH(esm.start_date) = %s
					AND YEAR(esm.start_date) = %s
					AND MONTH(esm.end_date) = %s
					AND YEAR(esm.end_date) = %s
				"""
			params = (employee.employee, start_month, start_year, end_month, end_year)
			sql = frappe.db.sql(query, params, as_dict=True)
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

