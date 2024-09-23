# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeShiftManagement(Document):
	
	def validate(self):
		self.check_employee_period()
		self.check_active_status()

	def on_submit(self):
		self.create_shift_assignment()


	def check_employee_period(self):
		sql = frappe.db.sql("""
				SELECT name , employee
				FROM `tabEmployee Shift Management` tesm 
				WHERE docstatus =1  AND employee = %s AND %s BETWEEN tesm.start_date AND tesm.end_date ;
			""", (self.employee , str(self.start_date)), as_dict=True)
		if sql and sql[0]:
			frappe.throw("""Employee:<b> {emp} </b> has Employee Shift Management : <b> {esm} </b>
				in the same period """.format(emp= sql[0]['employee'] , esm= sql[0]['name']) , 
				title=_("Exist Employee Shift Management"))

	
	def check_active_status(self):
		sql = frappe.db.sql("""
			SELECT name 
			FROM `tabEmployee Shift Management` tesm 
       		WHERE docstatus = 1 AND status = 'Active' 
			AND employee = %s """ , (self.employee) , as_dict=True)
		if sql and sql[0]:
			frappe.throw(f"Employee {str(self.employee)} Alredy Exist Active Status in {str(sql[0]['name'])}")

	def create_shift_assignment(self):
		result = frappe.db.sql ("""
        SELECT employee ,posting_date , start_date , end_date , saturday_st , sunday_st ,
            monday_st , tuesday_st , wednesday_st , thursday_st , 
            friday_st
            FROM `tabEmployee Shift Management` tesm 
            WHERE name = %s
        """ , (self.name) , as_dict =True)
		employee = result[0]['employee']
		start_date = result[0]['start_date']
		end_date = result[0]['end_date']
		posting_date = (result[0]['posting_date']).weekday()
		today = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][posting_date]
		active_day = today.lower()+"_st"
		active_shift = result[0][active_day]
		shift_type = list()
		shift_type.append(str(result[0]['saturday_st']))
		shift_type.append(str(result[0]['sunday_st']))
		shift_type.append(str(result[0]['monday_st']))
		shift_type.append(str(result[0]['tuesday_st']))
		shift_type.append(str(result[0]['wednesday_st']))
		shift_type.append(str(result[0]['thursday_st']))
		shift_type.append(str(result[0]['friday_st']))
		shift_type = list(set(shift_type))
		for i in shift_type:
			if 'None' in shift_type:
				shift_type.remove('None')
		shift_management = frappe.db.sql("""
		SELECT name  
		FROM `tabShift Assignment` tsa 
		WHERE employee = %s  AND status = 'Active' 
		""" , (employee), as_dict = True)
		if shift_management:
			for status in shift_management:
				shift_management_name = status.get('name')
				frappe.db.set_value('Shift Assignment' , shift_management_name , 'status', 'Inactive')
				doc = frappe.get_doc('Shift Assignment', shift_management_name)
				doc.save()

		for type in shift_type:
			shift = frappe.new_doc('Shift Assignment')
			shift.employee = employee
			shift.start_date = start_date
			shift.end_date = end_date
			shift.shift_type = type
			shift.custom_employee_shift_management = self.name
			if type == active_shift:
				shift.status = 'Active'
			else :
				shift.status = 'Inactive'
			shift.insert(ignore_permissions = True)
			shift.save()
			shift.submit()
		frappe.msgprint(f"Shift Assignments created for {employee} with types: {shift_type[0]}" ,alert=True)
