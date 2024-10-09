# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeDeductionBulk(Document):
    def validate(self):
        self.validation()
    def on_submit(self):
        self.create_deduction()
    
    def validation(self):
        if not self.by_amount and not self.by_percent:
            frappe.throw(
                _("Please select either By Amount or By Percent")
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
        self.employees = []
        employee_list = []
        cond = " te.status = 'Active' "
        if self.department:
            cond += f" AND te.department = '{self.department}'"
        if self.country:
            cond += f" AND te.custom_nationality = '{self.country}'"
        if self.designation:
            cond += f" AND te.designation = '{self.designation}'"
        if self.branch:
            cond += f" AND te.branch = '{self.branch}'"
        if self.employee_grade:
            cond += f" AND te.grade = '{self.employee_grade}'"
        if self.employment_type:
            cond += f" AND te.employment_type = '{self.employment_type}'"
        
        employees = frappe.db.sql(f"""
                SELECT 
                    te.name, 
                    te.employee_name, 
                    te.designation, 
                    te.grade, 
                    te.department, 
                    te.custom_nationality, 
                    te.branch, 
                    te.employment_type
                FROM tabEmployee te 
                WHERE {cond}
            """, as_dict=True)
        
        if not employees:
            frappe.throw(
                _("No employees found with the given filters")
                )

        for emp in employees:
            self.append('employees',{
                'employee': emp.name,
                'employee_name': emp.employee_name,
                'designation': emp.designation,
                'employee_grade': emp.grade,
                'department': emp.department,
                'country': emp.custom_nationality,
                'branch': emp.branch,
                'employment_type': emp.employment_type
            })
        self.no_of_employee = len(employees)
        self.save()
        return employee_list
    
    def create_deduction(self):
        for employee in self.employees:
            basic_salary_query = frappe.db.sql("""
                                            SELECT tescd.esc_amount, tc.default_currency 
                                            FROM tabEmployee te
                                            INNER JOIN `tabEmployee Salary Component Detail` tescd ON tescd.parent = te.name
                                            INNER JOIN tabCompany tc ON te.company = tc.name
                                            WHERE 
                                                tescd.salary_component = tc.custom_salary_component AND 
                                                te.name = %s AND tescd.is_active = 1
                                        """,(employee.employee), as_dict=True)
            if not basic_salary_query:
                frappe.msgprint(f"No active salary component found for employee {employee.employee}" , alert = True )
            if self.by_amount:
                deduction_amount = self.total
            elif self.by_percent:
                basic_salary = basic_salary_query[0]['esc_amount']
                deduction_amount = basic_salary * self.percentage
                
            new_deduction = frappe.new_doc('Employee Deduction')
            new_deduction.employee = employee.employee
            new_deduction.employee_name = employee.employee_name
            new_deduction.company = self.company
            new_deduction.department = employee.department
            new_deduction.bulk_ref = self.name
            new_deduction.salary_component = self.salary_component
            new_deduction.currency = basic_salary_query[0]['default_currency']
            new_deduction.payroll_date = self.posting_date
            new_deduction.deduction_amount = deduction_amount 
            new_deduction.save(ignore_permissions = True)
            new_deduction.submit()