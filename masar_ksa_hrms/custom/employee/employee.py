import frappe
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation

def validate(self , method):
    check_numbers_length(self)
    check_salary_components(self)
    check_basic_salary(self)
    
    
def check_salary_components(self):
    company = frappe.get_doc('Company' , self.company)
    company_sc = company.custom_salary_component
    if company_sc is None:
        frappe.throw("Set Defualt Salary Component for Basic Salary in Company.", title=_("Missing Company Salary Component"))
    for component in self.custom_employee_salary_component:
        if component.salary_component:
            same_components = [row for row in self.custom_employee_salary_component if row.salary_component == component.salary_component]
        if len(same_components) > 1:
            active_count = sum(1 for row in same_components if row.is_active)
            if active_count > 1:
                frappe.throw(f"Only one salary component: <b> {component.salary_component}</b> can be active." , title=_("Active Salary Component"))

                
def check_basic_salary(self):
    company = frappe.get_doc('Company' , self.company)
    company_sc = company.custom_salary_component
    if company_sc is None:
        frappe.throw("Set Defualt Salary Component for Basic Salary in Company.", title=_("Missing Company Salary Component"))
    basic_salary_exist = 0 
    for sc in self.custom_employee_salary_component:
        if (sc.salary_component == company_sc) and (sc.is_active == 1) and (sc.esc_amount != 0) :
            basic_salary_exist = 1 
    if basic_salary_exist == 0:
        frappe.throw(
            _("There is no Active Salary Component: <b>{0}</b> in the Employee Salary Component.").format(company_sc),
            title=_("Missing Salary Component")
        )

def check_numbers_length(self):
    if self.custom_nationality:
        if self.custom_nationality == "Saudi Arabia":
            self.custom_citizen_number = None
            if len(str(self.custom_nationality_number)) != 10:
                frappe.throw("Nationality Number Must be ten digits." ,  
                            title=_("Error Nationality Number") 
                )
        else:
            self.custom_nationality_number = None
            if len(str(self.custom_citizen_number)) != 10:
                frappe.throw("Citizen Number Must be ten digits." ,  
                            title=_("Error Citizen Number") 
                )
    if self.custom_is_social_security_applicable:
        if len(str(self.custom_ss_number)) != 9:
            frappe.throw("Social Security Number Must be nine digits." ,  
                            title=_("Error Social Security Number") 
                )