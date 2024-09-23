import frappe
from frappe import _
import datetime
from datetime import timedelta , datetime


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