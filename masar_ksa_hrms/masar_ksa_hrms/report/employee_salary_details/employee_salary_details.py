# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(), get_data(filters), None

def get_data(filters):
    _from, to = filters.get('from'), filters.get('to')
    conditions = " AND 1=1"
    if filters.get('ss_no'):
        conditions += f" AND tss.name LIKE '%{filters.get('ss_no')}'"
    if filters.get('company'):
        conditions += f" AND tss.company = '{filters.get('company')}'"
    if filters.get('emp_name'):
        conditions += f" AND tss.employee LIKE '%{filters.get('emp_name')}'"
    if filters.get('des'):
        conditions += f" AND tss.designation LIKE '%{filters.get('des')}'"
    if filters.get('branch'):
        conditions += f" AND tss.branch LIKE '%{filters.get('branch')}'"
    if filters.get('dep'):
        conditions += f" AND tss.department LIKE '%{filters.get('dep')}'"
    if _from and to:
        conditions += f" AND tss.start_date BETWEEN '{_from}' AND '{to}'"

    data = frappe.db.sql(f"""
                        SELECT DISTINCT
							tss.name AS `Salary Slip No.`,
							tss.employee AS `Employee No.`,
							tss.employee_name AS `Employee Name`,
							tss.branch AS `Branch`,
							tss.company AS `Company`,
							tss.department AS `Department`,
							tss.designation AS `Designation`,
							te.date_of_joining AS `Date of Joining`,
							tss.gross_pay AS `Reserved Salary`,
							tss.leave_without_pay AS `Leave Without Pay`,
							tss.payment_days AS `Payment Days`,
							MAX(CASE WHEN tsd.salary_component = 'Basic' THEN tsd.amount END) AS `Basic Salary`,
							tssa.base AS `Original Basic Salary`,
							MAX(CASE WHEN tsd.salary_component IN ('Overtime-Sales', 'Overtime-Production', 'Overtime-Management') THEN tsd.amount END) AS `Overtime Allowance`,
							(SELECT SUM(IF(tsd.salary_component NOT IN ('Overtime-Sales', 'Overtime-Production', 'Overtime-Management', 'Basic', 'Awards IN __ OUT', 'Non Taxable Bonus', 'End Service Awards', 'Project Awards', 'Award', 'Bonus IN-OUT'), tsd.amount, 0))
							FROM `tabSalary Detail` tsd
							WHERE tsd.parent = tss.name AND tsd.parentfield = 'earnings') AS `Other Earnings`,
							tss.gross_pay AS `Total Earnings`,
							MAX(CASE WHEN tsd.salary_component IN ('GOSI Deduction-Sales', 'GOSI Deduction-Production', 'GOSI Deduction-Management') THEN tsd.amount END) AS `GOSI`,
							(SELECT SUM(IF(tsd.salary_component NOT IN ('GOSI Deduction-Sales', 'GOSI Deduction-Production', 'GOSI Deduction-Management'), tsd.amount, 0))
							FROM `tabSalary Detail` tsd
							WHERE tsd.parent = tss.name AND tsd.parentfield = 'deductions') AS `Other Deductions`,
							tss.total_deduction AS `Total Deductions`,
							tss.net_pay AS `Net Pay`,
							DATE_FORMAT(tss.start_date , '%M') as `Posting Month` , 
							tss.mode_of_payment AS `Mod Of Payment`
						FROM
							`tabSalary Slip` tss
						INNER JOIN `tabSalary Detail` tsd ON tss.name = tsd.parent
						INNER JOIN `tabSalary Structure Assignment` tssa ON tssa.employee = tss.employee
						INNER JOIN `tabEmployee` te ON te.name = tss.employee
						INNER JOIN `tabSalary Slip` tss_sub ON tss_sub.name = tss.name
						WHERE
							tss.docstatus = 1 AND tss_sub.name = tss.name AND tssa.docstatus = 1 {conditions}
						GROUP BY
							tss.name, tss.net_pay, tssa.base
							;
				""")
    
    return data

def get_columns():
    return [
	   "Salary Slip No.: Link/Salary Slip:300",
	   "Employee No.:Link/Employee:200",
	   "Employee Name: Data:200",
	   "Branch: Data:200",
	   "Company: Data:300",
	   "Department: Data:200",
	   "Designation: Data:200",
	   "Date of Joining: Data:150 ",
	   "Reserved Salary: Currency:150",
	   "Leave Without Pay: Data:150",
	   "Payment Days: Data:150",
	   "Basic Salary: Currency:150",
	   "Original Basic Salary: Currency:150",
	   "Overtime Allowance: Currency:150",
	   "Other Earnings: Currency:150",
	   "Total Earnings: Currency:150",
	   "GOSI: Currency:150",
	   "Other Deductions: Currency:150",
	   "Total Deductions: Currency:150",
	   "Net Pay: Currency:150",
	   "Posting Month: Data/Posting Month:150",
	   "Mode Of Payment: Data/Mode Of Paymnet:150" 
	]