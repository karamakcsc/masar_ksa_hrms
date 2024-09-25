import frappe
from frappe import _
import datetime
from datetime import timedelta , datetime , date
from datetime import datetime
from dateutil.relativedelta import relativedelta

def period_validate(self):
        data = frappe.db.sql('''
        SELECT name FROM `tab{doc}`
        WHERE employee = %s AND posting_date BETWEEN %s AND %s AND docstatus = 1 AND name != %s
        '''.format(doc = self.doctype), (self.employee, self.from_date, self.to_date , self.name))
        return data


def date_period(self):
        try:
            if self.posting_date:
                posting_date = datetime.strptime(self.posting_date, '%Y-%m-%d').date()
                start_month = posting_date.replace(day=1)
                next_month = start_month.replace(day=28) + timedelta(days=4) 
                end_month = next_month - timedelta(days=next_month.day)
                self.from_date = start_month
                self.to_date = end_month
                return {
				'from_date': start_month, 
				'to_date' : end_month
				} 
            else : 
                self.from_date = None
                self.to_date = None
                return 1 
        except Exception as ex:
            frappe.throw(f'Error While Execute Get Date Period: {str(ex)}')
            
            
def create_additional_salary(data):
        additional_salary = frappe.new_doc('Additional Salary')
        additional_salary.employee = data.employee
        additional_salary.employee_name = data.employee_name
        additional_salary.department = data.department
        additional_salary.company = data.company
        additional_salary.is_recurring = data.is_recurring
        additional_salary.payroll_date = data.payroll_date
        additional_salary.salary_component =  data.salary_component
        additional_salary.type  = data.type
        additional_salary.amount =  data.amount
        additional_salary.deduct_full_tax_on_selected_payroll_date =  data.deduct_full_tax_on_selected_payroll_date
        additional_salary.overwrite_salary_structure_amount = data.overwrite_salary_structure_amount
        additional_salary.ref_doctype = data.ref_doctype
        additional_salary.ref_docname = data.ref_docname
        additional_salary.insert(ignore_permissions=True)
        additional_salary.submit()
        return additional_salary
    
def eos_validation(self, table_name, rate_name):
    next_year = None
    last_row = len(getattr(self, table_name))
    
    for reg in getattr(self, table_name):
        
        rate = getattr(reg, rate_name)
        if rate > 100:
            frappe.throw(
                _("Rate cannot exceed 100. In Row {idx}"
                  .format(idx=reg.idx)
                  ), 
                title=_("Rate Error")
            )
        
        if reg.idx < last_row and reg.has_period and  reg.from_year >= reg.to_year:
            frappe.throw(
                _("The From Year in Row {idx} must be less than To Year."
                  .format(idx=reg.idx)
                  ), 
                title=_("Year Range Error")
            )
        
        if next_year is not None:
            if reg.from_year < next_year:
                frappe.throw(
                    _("The From Year in Row {idx} cannot be less than the To Year of the previous row (Row {previous_idx})."
                      .format(idx=reg.idx, previous_idx=reg.idx - 1)
                    ), 
                    title=_("Year Range Error")
                )
            elif reg.from_year > next_year:
                frappe.throw(
                    _("The From Year in Row {idx} must be equal to the To Year of the previous row (Row {previous_idx}). It should be {next_year}."
                      .format(idx=reg.idx, previous_idx=reg.idx - 1, next_year=next_year)
                    ), 
                    title=_("Year Range Error")
                )
        
        if reg.idx == last_row:
            if reg.has_period != 0:
                frappe.throw(
                    _("The Has Period in the last row must be set to 0."), 
                    title=_("Period Error")
                )
            if reg.to_year:
                frappe.throw(
                    _("The last row should not have a To Year value."), 
                    title=_("Year Error")
                )
        else:
            if reg.has_period != 1:
                frappe.throw(
                    _("All Rows Except the Last one Must Have Has Period set to 1. In Row {idx}"
                      .format(idx=reg.idx)), 
                    title=_("Period Error")
                )
            if not reg.to_year:
                frappe.throw(
                    _("All Rows with Has Period set to 1 must have a To Year value. In Row {idx}"
                      .format(idx=reg.idx)), 
                    title=_("Year Error")
                )
        
        next_year = reg.to_year

def get_date_details(from_date_str , to_date_str):
    from_date = datetime.strptime(str(from_date_str), '%Y-%m-%d').date()
    to_date = datetime.strptime(str(to_date_str), '%Y-%m-%d').date()
    delta = relativedelta(to_date, from_date)
    years = delta.years
    months = delta.months
    days = delta.days
    number_of_days_in_period = (to_date - from_date).days + 1 
    return number_of_days_in_period , years, months, days   


def get_number_of_days_in_year(from_date_str , to_date_str):
    payroll_settings = frappe.get_doc('Payroll Settings')
    working_day_30 = payroll_settings.working_day_30
    number_of_days_in_period , years, months, days = get_date_details(from_date_str , to_date_str)
    if working_day_30 == 1 :
        period_days = years * 360 + months * 30 + days
    else: 
        period_days = number_of_days_in_period
    return period_days , years, months, days