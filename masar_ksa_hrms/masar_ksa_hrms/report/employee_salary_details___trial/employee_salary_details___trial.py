# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import  Sum , Max , DateFormat

def execute(filters=None):
	return get_columns(), get_data(filters), None

def get_data(filters):
    sd = frappe.qb.DocType('Salary Detail')
    ss = frappe.qb.DocType('Salary Slip')
    ssa = frappe.qb.DocType('Salary Structure Assignment')
    e = frappe.qb.DocType('Employee')
    ss_sub = frappe.qb.DocType('Salary Slip')
    data = (frappe.qb.from_(ss)
		.join(sd)
  		.on(sd.parent == ss.name)
		.join(ssa)
		.on(ssa.employee == ss.employee)
		.join(e)
		.on(e.name == ss.employee)
		.join(ss_sub).on(ss_sub.name == ss.name)
		.where(ss.docstatus == 0 )
		.where(ss_sub.name == ss.name)
		.where(ssa.docstatus ==1 )
		.groupby(ss.name, ss.net_pay , ssa.base)
      .select(
        (ss.name.as_('Salary Slip No.')) , 
        (ss.employee.as_('Employee No.')) , 
        (ss.employee_name.as_('Employee Name')) , 
        (ss.branch.as_('Branch')) , 
        (ss.company.as_('Company')) , 
        (ss.department.as_('Department')) , 
        (ss.designation.as_('Designation')) , 
        (e.date_of_joining.as_('Date of Joining')) , 
        (ss.gross_pay.as_('Reserved Salary')) , 
        (ss.leave_without_pay.as_('Leave Without Pay')) , 
        (ss.payment_days.as_('Payment Days')) , 
        ((Max(
            frappe.qb.terms.Case()
            .when(
                (sd.salary_component == 'Basic'),
                (sd.amount)
                )
		)).as_('Basic Salary')), 
        (ssa.base.as_('Original Basic Salary')) , 
         ((Max(
			frappe.qb.terms.Case()
   				.when(
					(sd.salary_component.isin(['Overtime-Sales', 'Overtime-Production', 'Overtime-Management'])) ,
     				(sd.amount)
         )
				)
		).as_('Overtime Allowance')) , 
        (
			(
       			frappe.qb.from_(sd).select(
          			Sum(
							frappe.qb.terms.Case()
							.when(sd.salary_component.isin([
										'Overtime-Sales', 'Overtime-Production', 'Overtime-Management', 
										'Basic', 'Awards IN __ OUT', 'Non Taxable Bonus', 'End Service Awards', 
										'Project Awards', 'Award', 'Bonus IN-OUT'
													]), 0)  
							.else_(sd.amount)
              		)
				)
				.where(sd.parent == ss.name)
				.where(sd.parentfield == 'earnings')
          	).as_("Other Earnings")
		),
		(ss.gross_pay.as_('Total Earnings')) , 
		((Max(
			frappe.qb.terms.Case()
				.when(
        		(sd.salary_component.isin(['GOSI Deduction-Sales', 'GOSI Deduction-Production', 'GOSI Deduction-Management'])) , 
          		(sd.amount))
				)).as_('GOSI')
   		) ,
		(
			(
				frappe.qb.from_(sd).select(
					(Sum(
						frappe.qb.terms.Case()
							.when(sd.salary_component.isin([
									'GOSI Deduction-Sales', 'GOSI Deduction-Production', 'GOSI Deduction-Management'
									]),
							(sd.amount)
            			)
            			.else_(0) 
						))
					).where(sd.parent == ss.name)
					.where(sd.parentfield == 'deductions')
       			).as_('Total Deductions')
		) ,  
  		(ss.total_deduction.as_('Total Deductions')) , 
    	(ss.net_pay.as_('Net Pay')) , 
		(DateFormat(ss.start_date, '%M').as_('Posting Month')) , 
		(ss.mode_of_payment.as_('Mode of Payment'))
        )
	)
    if filters.get('from') and  filters.get('to') : 
        data = data.where(ss.start_date.between(filters.get('from'),filters.get('to')))
    if filters.get('ss_no'):
        data = data.where(ss.name == filters.get('ss_no'))
    if filters.get('company'):
        data = data.where(ss.company == filters.get('company'))
    if filters.get('emp_name'):
        data = data.where(ss.employee == filters.get('emp_name'))
    if filters.get('des'):
        data = data.where(ss.designation == filters.get('des'))   
    if filters.get('branch'):
        data = data.where(ss.branch == filters.get('branch'))  
    if filters.get('dep'):
        data = data.where(ss.department == filters.get('dep'))
    return data.run()

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
	   "Total Earnings: Currency:150"
	   "GOSI: Currency:150",
	   "Other Deductions: Currency:150",
	   "Total Deductions: Currency:150",
	   "Net Pay: Currency:150",
	   "Posting Month: Data/Posting Month:150",
	   "Mode of Payment: Data/Mode of Payment"
	]
