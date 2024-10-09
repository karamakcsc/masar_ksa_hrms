# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None

def data(filters):
    conditions = "1=1"
    
    _from, to = filters.get('from'), filters.get('to')
    
    if filters.get('employee'):
        conditions += f" AND te.employee = '{filters.get('employee')}'"
        
    if filters.get('salary_component'):
        conditions += f" AND tschd.salary_component = '{filters.get('salary_component')}'"
        
    if filters.get('is_active'):
        conditions += f" AND tschd.is_active = '{filters.get('is_active')}'"
        
    if _from and to:
        conditions += f" AND tschd.from_date BETWEEN '{_from}' AND '{to}'"
        
    data = frappe.db.sql(f"""
                        	SELECT 
								te.employee, te.employee_name, te.department, te.company, te.status, tschd.salary_component,
								tschd.amount, tschd.from_date, tschd.is_active, tschd.escm_ref
							FROM tabEmployee te
							INNER JOIN `tabEmployee Salary Component History` tesch ON tesch.employee = te.employee
							INNER JOIN `tabSalary Component History Details` tschd ON tschd.parent = tesch.name
							WHERE {conditions}
						""")
    
    return data

def columns():
    return [
		"Employee: Link/Employee:150",
		"Employee Name: Data:250",
		"Department: Link/Department:150",
		"Company: Link/Company:150",
		"Status: Data:125",
		"Salary Component: Link/Salary Component:150",
		"Amount: Currency:100",
		"From Date: Date:150",
		"Is Active: Check:100",
		"Employee Salary Component Management: Link/Employee Salary Component Management:350",
	]
