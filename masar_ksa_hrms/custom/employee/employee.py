import frappe
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation

def validate(self , method):
    check_numbers_length(self)
    check_salary_components(self)
    # check_basic_salary(self)
    calculate_salaries(self)
    eos_validation(self ,table_name = 'custom_emp_eso_periods_table' , rate_name = 'salary_rate')

def check_salary_components(self):
    for component in self.custom_employee_salary_component:
        if component.salary_component:
            same_components = [row for row in self.custom_employee_salary_component if row.salary_component == component.salary_component]
        if len(same_components) > 1:
            active_count = sum(1 for row in same_components if row.is_active)
            if active_count > 1:
                frappe.throw(f"Only one salary component: <b> {component.salary_component}</b> can be active." , title=_("Active Salary Component"))

                
# def check_basic_salary(self):
#     company = frappe.get_doc('Company' , self.company)
#     company_sc = company.custom_salary_component
#     if company_sc is None:
#         frappe.throw("Set Defualt Salary Component for Basic Salary in Company.", title=_("Missing Company Salary Component"))
#     basic_salary_exist = 0 
#     for sc in self.custom_employee_salary_component:
#         if (sc.salary_component == company_sc) and (sc.is_active == 1) and (sc.esc_amount != 0) :
#             basic_salary_exist = 1 
#     if basic_salary_exist == 0:
#         frappe.throw(
#             _("There is no Active Salary Component: <b>{0}</b> in the Employee Salary Component.").format(company_sc),
#             title=_("Missing Salary Component")
#         )

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
        if len(self.custom_ss_number) != 9:
            frappe.throw("Social Security Number Must be nine digits." ,  
                            title=_("Error Social Security Number") 
                )
            
def calculate_salaries(self):
    basic_amount = 0 
    basic_with_allowance = 0 
    deduction_salary = 0 
    ss_salary = 0
    eos_salary = 0 
    company = frappe.get_doc('Company', self.company)
    ss_rate_sa = company.custom_emp_ss_sa_rate / 100
    ss_rate_other = company.custom_emp_ss_other_rate /100
    default_basic_comp = company.custom_salary_component
    for amount in self.custom_employee_salary_component:
        sal_comp = frappe.get_doc('Salary Component', amount.salary_component)
        if default_basic_comp == amount.salary_component :
            if amount.is_active == 1 :
                basic_amount = amount.esc_amount
                basic_with_allowance += amount.esc_amount
                deduction_salary += amount.esc_amount
                ss_salary  += amount.esc_amount
                eos_salary += amount.esc_amount
        else:
            if sal_comp.custom_is_overtime_applicable == 1 :
                                                                basic_with_allowance += amount.esc_amount
            if sal_comp.custom_salary_deduction == 1 :
                                                                deduction_salary += amount.esc_amount
            if sal_comp.custom_is_ss_applicable == 1 :
                                                                ss_salary  += amount.esc_amount
            if sal_comp.custom_is_eos_applicable == 1 :
                                                                eos_salary += amount.esc_amount 

#################### End Calculation ####################

    self.custom_basic_salary = basic_amount
    self.custom_salary_deduction = deduction_salary
    self.custom_basic_salary_with_allowance = basic_with_allowance
    self.custom_eos_salary = eos_salary
    if self.custom_nationality == 'Saudi Arabia':
                                    ss_amount = ss_salary * ss_rate_sa
    else:
        if ss_rate_other == 0 : 
                                    ss_amount = 0 
        else:
                                    ss_amount = ss_salary * ss_rate_other    
    self.custom_ss_amount = ss_amount