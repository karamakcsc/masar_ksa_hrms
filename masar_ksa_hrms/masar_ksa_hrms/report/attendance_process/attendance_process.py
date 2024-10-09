# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None

def data(filters):
    conditons = "tap.docstatus = 1"
    
    _from, to = filters.get('from'), filters.get('to')
    
    if filters.get('employee'):
        conditons += f" AND tap.employee = '{filters.get('employee')}'"
        
    if filters.get('department'):
        conditons += f" AND tap.department = '{filters.get('department')}'"
        
    if _from and to:
        conditons += f" AND tap.posting_date BETWEEN '{_from}' AND '{to}'"
        
    data = frappe.db.sql(f"""
                        	SELECT
								tap.employee, tap.employee_name, tap.department, tap.posting_date,
								tap.from_date, tap.to_date, tap.working_day, tap.basic_salary, tap.basic_salary_with_allowances,
								tap.leaves_salary, tap.bs_hour_rate, tap.bswa_hour_rate, tap.leaves_hour_rate,
								tap.ot_total_amount, tap.total_amount
							FROM `tabAttendance Process` tap
							WHERE {conditons}
                         """)
    return data

def columns():
    return [
		"Employee: Link/Employee:150",
		"Employee Name: Data:250",
		"Department: Link/Department:150",
		"Posting Date: Date:150",
		"From Date: Date:150",
		"To Date: Date:150",
		"Working Day: Float:150",
		"Basic Salary: Currency:250",
		"Overtime Salary: Currency:250",
		"Leaves Salary: Currency:150",
		"Basic Salary Hour Rate: Float:250",
		"Overtime Hour Rate: Float:200",
		"Leaves Hour Rate: Float:200",
		"Total Amount For Overtime: Float:250",
		"Total Amount For Leaves: Float:250",
	]
