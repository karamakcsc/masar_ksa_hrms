# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import date_period

class SalariesIncrement(Document):
    def validate(self):
        if not self.by_amount and not self.by_percent:
            frappe.throw(_("Please select either By Amount or By Percent"))

        if self.by_amount and self.by_percent:
            frappe.throw(_("You cannot select both By Amount and By Percent at the same time"))
            
        if self.by_amount and (self.total is None or self.total <= 0):
            frappe.throw(_("The 'Total' value must be greater than zero"))

        if self.by_percent and (self.percentage is None or self.percentage <= 0 or self.percentage > 100):
            frappe.throw(_("The 'Percentage' value must be greater than zero and not exceed 100"))
            
    def on_submit(self):
        self.transfer_to_employee()

    def transfer_to_employee(self):
        mapping_field_name = {
            'Department' : 'department',
            'Country' : 'custom_nationality',
            'Designation' : 'designation', 
            'Branch' : 'branch',
            'Employee Grade' : 'grade',
            'Employment Type' : 'employment_type'
        }
        
        document_type = self.document_type
        field_name = mapping_field_name.get(document_type)
        employees = frappe.db.sql(f"SELECT name FROM `tabEmployee` WHERE {field_name} = '{self.doctype_name}' AND status = 'Active'" , as_dict=1)
        
        if not employees or len(employees) == 0:
            frappe.throw(_("No employees found for the document type: {0}").format(self.document_type))
            
        for employee in employees:
            emp_doc = frappe.get_doc("Employee", employee.name)
             
            for component in emp_doc.custom_employee_salary_component:
                if component.salary_component == self.salary_component and component.is_active == 1:
                    component.is_active = 0
                    
            emp_doc.append("custom_employee_salary_component", {
                "salary_component": self.salary_component,
                "is_active": 1,
                "esc_amount": self.total,
                "date": self.posting_date,
                "remarks": f"Added By Salaries INC. From Number ({self.name})"
            })

            # date_period_data = date_period(self)
            # from_date = date_period_data['from_date']
            # to_date = date_period_data['to_date']
        
            # company_doc = frappe.get_doc('Company', self.company)
            # custom_salary_component = company_doc.custom_salary_component 
            # if not custom_salary_component:
            #     frappe.throw(_("Default Custom Salary Component is not set in Company settings."))
            #     return 

            # for component in emp_doc.custom_employee_salary_component:
            #     if self.is_overtime_applicable == 1:
            #         if self.is_overtime_applicable == component.custom_is_overtime_applicable:
            #             if self.percentage and self.percentage > 0:
            #                 component.esc_amount += (component.esc_amount * (self.percentage / 100))
            #                 component.remarks = f"Updated by percentage ({self.percentage}%) from Salaries Increment {self.name}"
            #     else:
            #         if self.percentage and self.percentage > 0:
            #             component.esc_amount += (component.esc_amount * (self.percentage / 100))
            #             component.remarks = f"Updated by percentage ({self.percentage}%) from Salaries Increment {self.name}"
            
            emp_doc.save()

        frappe.msgprint(_("Data has been successfully transferred to the employees' salary components."))

    # def apply_increment(self, emp_doc):
    #     for component in emp_doc.custom_employee_salary_component:
    #         if component.salary_component == self.salary_component and component.is_active == 1:
    #             component.is_active = 0
                
    #     for component in emp_doc.custom_employee_salary_component:
    #         if self.is_overtime_applicable == 1 and component.custom_is_overtime_applicable == 1:

    #             component.esc_amount += component.esc_amount * (self.percentage / 100)
    #         elif self.is_overtime_applicable != 1:

    #             component.esc_amount += component.esc_amount * (self.percentage / 100)

    #     emp_doc.append("custom_employee_salary_component", {
    #         "salary_component": self.salary_component,
    #         "is_active": 1,
    #         "esc_amount": self.total,
    #         "date": self.posting_date,
    #         "remarks": f"Added By Salaries INC. From Number ({self.name})"
    #     })
        
        