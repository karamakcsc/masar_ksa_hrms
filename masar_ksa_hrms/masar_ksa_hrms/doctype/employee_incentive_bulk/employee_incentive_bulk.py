import frappe
from frappe.model.document import Document
from frappe import _

class EmployeeIncentiveBulk(Document):
    def validate(self):
        self.validation()
    
    def on_submit(self):
        self.create_employee_incentive()    
        

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
            frappe.throw(_("No employees found with the given filters"))

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
    
    def validation(self):
        if not self.by_amount and not self.by_percent:
            frappe.throw(_("Please select either By Amount or By Percent"))

        if self.by_amount and self.by_percent:
            frappe.throw(_("You cannot select both By Amount and By Percent at the same time"))
            
        if self.by_amount and (self.total is None or self.total <= 0):
            frappe.throw(_("The 'Total' value must be greater than zero"))

        if self.by_percent and (self.percentage is None or float(self.percentage) <= 0 or float(self.percentage) > 100):
            frappe.throw(_("The 'Percentage' value must be greater than zero and not exceed 100"))
        
    def create_employee_incentive(self):
        
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
                incentive_amount = self.total
            elif self.by_percent:
                basic_salary = basic_salary_query[0]['esc_amount']
                incentive_amount = basic_salary * self.percentage
                
            new_incentive = frappe.new_doc('Employee Incentive')
            new_incentive.employee = employee.employee
            new_incentive.employee_name = employee.employee_name
            new_incentive.company = self.company
            new_incentive.department = employee.department
            new_incentive.custom_bulk_ref = self.name
            new_incentive.salary_component = self.salary_component
            new_incentive.currency = basic_salary_query[0]['default_currency']
            new_incentive.payroll_date = self.posting_date
            new_incentive.incentive_amount = incentive_amount 
            new_incentive.save(ignore_permissions = True)
            new_incentive.submit()