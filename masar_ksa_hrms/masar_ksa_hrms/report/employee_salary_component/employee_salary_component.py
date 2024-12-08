# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return columns(), data(filters), None

def data(filters):
    e = frappe.qb.DocType('Employee')
    esch = frappe.qb.DocType('Employee Salary Component History')
    schd = frappe.qb.DocType('Salary Component History Details')
    query = (
        frappe.qb.from_(e)
        .join(esch)
        .on(esch.employee == e.name)
        .join(schd)
        .on(schd.parent == esch.name)
        .select(
            (e.name),
            (e.employee_name),
            (e.department),
            (e.company),
            (e.status),
            (schd.salary_component),
            (schd.amount),
            (schd.from_date),
            (schd.is_active),
            (schd.escm_ref)
		) 
	)
    if filters.get('from') and  filters.get('to'):
        query = query.where(schd.from_date.between(filters.get("from_date"), filters.get("to_date")))
    query=query.where(e.employee == filters.get('employee')) if filters.get('employee') else query=query
    query=query.where(schd.salary_component == filters.get('salary_component')) if filters.get('salary_component') else query=query
    query=query.where(schd.is_active == filters.get('is_active')) if filters.get('is_active') else query=query
    return query.run()
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
