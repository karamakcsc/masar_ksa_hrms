# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None

def data(filters):
    conditions = "tsla.docstatus = 1"
    
    _from, to = filters.get('from'), filters.get('to')
    
    if filters.get('employee'):
        conditions += f" AND tsla.employee = '{filters.get('employee')}'"
        
    if filters.get('leave_approver'):
        conditions += f" AND tsla.leave_approver = '{filters.get('leave_approver')}'"
        
    if filters.get('shift_assignment'):
        conditions += f" AND tsla.shift_assignment = '{filters.get('shift_assignment')}'"
        
    if _from and to:
        conditions += f" AND tsla.leave_date BETWEEN '{_from}' AND '{to}'"
        
    data = frappe.db.sql(f"""
                        SELECT 
							tsla.employee, tsla.employee_name, tsla.department, tsla.leave_approver, tsla.shift_assignment,
							CASE 
								WHEN tsla.salary_deduction = 1 THEN 'Salary Deduction'
								WHEN tsla.balance_deduction = 1 THEN 'Balance Deduction'
								WHEN tsla.none_deduction = 1 THEN 'None Deduction'
								ELSE 'No Deduction'
							END AS deduction_type, 
							tsla.leave_date, tsla.from_time, tsla.to_time, tsla.status 
						FROM `tabShort Leave Application` tsla 
						WHERE {conditions}
                         """)
    
    return data

def columns():
    return [
		"Employee: Link/Employee:150",
		"Employee Name: Data:250",
		"Department: Link/Department:150",
		"Leave Approver: Link/User:200",
		"Shift Assignment: Link/Shift Assignment:200",
		"Deduction Type: Data:200",
		"Leave Date: Date:150",
		"From Time: Time:150",
		"To Time: Time:150",
		"Status: Data:150",
	]
