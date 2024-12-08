# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeDeductionBulk(Document):
    def validate(self):
        self.check_validations()
    def on_submit(self):
        self.create_employee_details()
    
    def check_validations(self):
        if (self.by_amount + self.by_percent) != 1:
            frappe.throw(
                _("Please select One either By Amount or By Percent")
                )
        if self.by_amount and self.by_percent:
            frappe.throw(
                _("You cannot select both By Amount and By Percent at the same time")
                )
        if self.by_percent and (self.percentage is None or float(self.percentage) <= 0 or float(self.percentage) > 100):
            frappe.throw(
                _("The 'Percentage' value must be greater than zero and not exceed 100")
                )
            
    @frappe.whitelist()
    def get_employees(self):
        e = frappe.qb.DocType('Employee')
        employees_query = (
            frappe.qb.from_(e)
            .select(
                (e.name),
                (e.employee_name),
                (e.designation),
                (e.grade),
                (e.department),
                (e.custom_nationality),
                (e.branch),
                (e.employment_type)
            )
            .where(e.status =='Active')
        )
        if self.department:
            employees_query = employees_query.where(e.department == self.department)
        if self.country:
            employees_query = employees_query.where(e.custom_nationality == self.country)
        if self.designation:
            employees_query = employees_query.where(e.designation == self.designation)
        if self.branch:
            employees_query = employees_query.where(e.branch == self.branch)
        if self.employee_grade:
            employees_query = employees_query.where(e.grade == self.employee_grade)
        if self.employment_type:
            employees_query = employees_query.where(e.employment_type == self.employment_type)
      
        employees = employees_query.run(as_dict = True)
        if len(employees) == 0:
            frappe.msgprint(
                'There No Employees found with the Given Filters.',
                alert = True , 
                indicator='blue'
            )
            self.employees = list()
            self.no_of_employee = 0
            return True
        else: 
            self.employees = list()
            self.no_of_employee = len(employees)
            for e in employees:
                self.append('employees',{
                'employee': e.name,'employee_name': e.employee_name,'designation': e.designation,'employee_grade': e.grade,'department': e.department,
                'nationality': e.custom_nationality,'branch': e.branch,'employment_type': e.employment_type
                    }
                )
            return True  
    def create_employee_details(self):
        e = frappe.qb.DocType('Employee')
        c = frappe.qb.DocType('Company')
        data = (
                frappe.qb.from_(e)
                .join(c)
                .on(c.name == e.company)
                .select(
                    (e.name.as_('employee')), (e.employee_name) , (c.name.as_('company')),
                    (e.department) , (c.default_currency.as_('currency')),
                    ((e.custom_basic_salary).as_('deduction_amount' if self.doctype == 'Employee Deduction Bulk' else 'incentive_amount'))
                )
                .where(e.name.isin([e.employee for e in self.employees]))
        ).run(as_dict = True)
        for d in data:
            d['bulk_ref' if self.doctype == 'Employee Deduction Bulk' else 'custom_bulk_ref'] = self.name
            d['salary_component'] = self.salary_component
            d['payroll_date'] = self.posting_date
            if self.by_percent:
                d['deduction_amount' if self.doctype == 'Employee Deduction Bulk' else 'incentive_amount'] =( 
                    d['deduction_amount' if self.doctype == 'Employee Deduction Bulk' else 'incentive_amount'] * self.percentage / 100
                )
            elif self.by_amount:
                d['deduction_amount' if self.doctype == 'Employee Deduction Bulk' else 'incentive_amount'] = self.amount
            name_without_bulk = self.doctype.replace(' Bulk', '')
            frappe.new_doc(name_without_bulk).update(d).save(ignore_permissions=True).submit()