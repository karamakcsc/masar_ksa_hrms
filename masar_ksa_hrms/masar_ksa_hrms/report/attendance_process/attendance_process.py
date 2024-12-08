# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None




def data(filters):
    ap = frappe.qb.DocType('Attendance Process')
    query = (
        frappe.qb.from_(ap)
        .select(
            (ap.employee), 
            (ap.employee_name), 
            (ap.department), 
            (ap.posting_date),
			(ap.from_date), 
            (ap.to_date), 
            (ap.working_day), 
            (ap.basic_salary), 
            (ap.basic_salary_with_allowances),
			(ap.leaves_salary), 
            (ap.bs_hour_rate), 
            (ap.bswa_hour_rate), 
            (ap.leaves_hour_rate),
			(ap.ot_total_amount), 
            (ap.total_amount)
		)
	)
    if filters.get('from') and filters.get('to'):
        query  = query.where(ap.posting_date.between(filters.get("from_date"), filters.get("to_date")) )
    
    query = query.where(ap.employee == filters.get('employee')) if filters.get('employee') else query=query
    query = query.where(ap.department == filters.get('department')) if filters.get('department') else query=query
    return query.run()
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
	
