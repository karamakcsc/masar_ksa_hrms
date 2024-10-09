# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.hr.utils import validate_active_employee
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import create_additional_salary 

class EmployeeDeduction(Document):
    def on_submit(self):
        self.additional_salary()
    
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_salary_structure()

    def validate_salary_structure(self):
            if not frappe.db.exists("Salary Structure Assignment", {"employee": self.employee}):
                frappe.throw(
                    frappe._("There is no Salary Structure assigned to {0}. First assign a Salary Stucture.").format(
                        self.employee
				)
			)
    def additional_salary(self):
        data = {
            'employee' :  self.employee, 
            'employee_name' :  self.employee_name, 
            'department' : self.department, 
            'company' : self.company,
            'is_recurring' : 0 ,
            'payroll_date' : self.payroll_date , 
            'salary_component' : self.salary_component , 
            'type' : "Deduction",
            'amount' : self.deduction_amount , 
            'deduct_full_tax_on_selected_payroll_date' : 1 ,
            'overwrite_salary_structure_amount' : 1 , 
            'ref_doctype' : self.doctype , 
            'ref_docname' : self.name
        }
        name = create_additional_salary(data = data)
        frappe.msgprint(f'Additional Salary :{name} Created Successfully.', 
                        alert = True , 
                        indicator='green'
            )
