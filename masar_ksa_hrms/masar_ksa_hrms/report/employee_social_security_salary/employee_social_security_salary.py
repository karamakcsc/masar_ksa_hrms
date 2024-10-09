# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None

def data(filters):
    conditions = ""
    
    _from, to = filters.get('from'), filters.get('to')
    
    if filters.get('employee'):
        conditions += f" AND te.employee = '{filters.get('employee')}'"
        
    if filters.get('is_active'):
        conditions += f" AND tescd.is_active = '{filters.get('is_active')}'"
        
    if _from and to:
        conditions += f" AND te.custom_ss_start_date BETWEEN '{_from}' AND '{to}'"
        
    data = frappe.db.sql(f"""
						SELECT 
							te.employee, te.employee_name, te.department, te.custom_ss_number, te.custom_ss_start_date, 
							te.custom_basic_salary, SUM(tescd.esc_amount), te.custom_ss_salary, te.custom_ss_amount, tescd.`date`, tescd.is_active
						FROM tabEmployee te
						INNER JOIN `tabEmployee Salary Component Detail` tescd ON tescd.parent = te.name
						INNER JOIN `tabSalary Component` tsc ON tsc.name = tescd.salary_component
						WHERE tsc.custom_is_ss_applicable = 1 AND te.custom_is_social_security_applicable = 1 {conditions}
						GROUP BY te.employee
                         """)
    
    return data

def columns():
    return [
		"Employee: Link/Employee:150",
		"Employee Name: Data:200",
		"Department: Link/Department:150",
		"Social Security Number: Int:200",
		"Social Security Start Date: Date:200",
		"Basic Salary: Float:150",
		"Social Security Earnings: Float:200",
		"Social Security Salary: Float:200",
		"Social Security Amount: Float:200",
		"Salary Component Date: Date:200",
		"Is Active: Check:100",
	]
