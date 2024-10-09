# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeSalaryComponentManagement(Document):  
          
    @frappe.whitelist()
    def calculate_ss_amount(self):
        if not self.employee:
            frappe.msgprint('Please Set Employee For Get Calculations.' , 
                            title = frappe._("Missing Employee")
                            )
            return 
        
        if self.ss_salary in [None , 0 ,'0' , '']:
            return 0
        elif self.ss_salary < 0 : 
            frappe.msgprint("Social Security salary must be greater than zero.",
                            title = frappe._("Salary Validation")
                            )
            return 
        dict_rate = self.get_ss_rate()
        rate = float(dict_rate.emp_rate)
        if rate == 0 or rate is None:
            ss_amount =0 
        else:      
            ss_amount = float(self.ss_salary) * rate
        self.ss_amount = ss_amount
        return ss_amount
        
    def get_ss_rate(self):
        emp_doc = frappe.get_doc('Employee' , self.employee)
        if  self.default_ss == 0 :
            return frappe._dict({
                 'emp_rate' : float(self.emp_ss_rate)/100 , 
                 'comp_rate' : float(self.comp_ss_rate)/100
                }   
            )
        else:      
            if self.company:
                company_doc = frappe.get_doc('Company' , self.company)
            else:
                company_doc = frappe.get_doc('Company' , emp_doc.company)
                
            if emp_doc.custom_nationality == 'Saudi Arabia':
                
                emp_rate = float(company_doc.custom_emp_ss_sa_rate)/100
                comp_rate = float(company_doc.custom_comp_ss_sa_rate)/100
            else:
                emp_rate = float(company_doc.custom_emp_ss_other_rate) /100   
                comp_rate = float(company_doc.custom_comp_ss_other_rate)/100    
            return frappe._dict(
                {
                'emp_rate' :emp_rate , 
                'comp_rate' : comp_rate
                }
            )
        
    @frappe.whitelist()
    def get_basic_salary_component(self):
        if self.company:
            default_sc_sql = frappe.db.sql("""
                                       SELECT custom_salary_component FROM tabCompany tc 
                                       WHERE name = %s
                                       """ , (self.company) , as_dict = True)
            if len(default_sc_sql) != 0 : 
                return default_sc_sql[0]['custom_salary_component']
            else: 
                return None
        elif self.employee:
            emp_doc = frappe.get_doc('Employee' , self.employee )
            if emp_doc.company:
                comp_doc = frappe.get_doc('Company' , emp_doc.company)
                salary_component = comp_doc.custom_salary_component
                return salary_component
            else :
                return None
        else:
            return None 
                
    @frappe.whitelist()
    def get_emp_social_security_info(self):
        if self.employee:
            ss_number_sql = frappe.db.sql("""
                SELECT custom_ss_number , custom_ss_start_date
                FROM tabEmployee 
                WHERE name = %s
            """, (self.employee), as_dict=True)
            if len(ss_number_sql) != 0:
                ss_number = ss_number_sql[0]['custom_ss_number']
                ss_date =  ss_number_sql[0]['custom_ss_start_date']
            else:
                ss_number = None
                ss_date = None
        else:
            ss_number = None
            ss_date = None
        
        return {
                'number' : ss_number,
                'date' : ss_date
                }
    @frappe.whitelist()
    def get_housing_percentage(self):
        if not self.employee:
            frappe.msgprint('Please Set Employee For Get Calculations.' , 
                            title = frappe._("Missing Employee")
                            )
            return 
        if not self.marital_status:
            frappe.msgprint('Please add Marital status for Employee:{emp} , to get true Calculation.'
                            .format(emp = self.employee),
                            title = frappe._("Missing Martial Status")
                            )
            return
        company_doc = frappe.get_doc('Company' , self.company)
        percent = 0 
        signle_percent = (float(company_doc.custom_single_housing_percent))
        married_percent = (float(company_doc.custom_married_housing_percent))
        if self.marital_status in ['Single' , 'Married']:
            if self.marital_status == 'Single':
                percent =signle_percent
            elif self.marital_status == 'Married':
                percent = married_percent
        else:
            if company_doc.custom_default_housing_percent == 'Single':
                percent = signle_percent
            elif  company_doc.custom_default_housing_percent =='Married':
                percent = married_percent        
        self.percentage = percent
        return float(percent)
           
    @frappe.whitelist()
    def get_housing_amount(self):
        if self.percentage is None or float(self.percentage) <= 0 :
            return 0 
        elif float(self.basic_salary) <= 0:
            return 0 
        else:
            if self.percentage : 
                percent_cal = float(self.percentage)
            if percent_cal == 0 or percent_cal is None:
                self.housing_amount = 0 
                return 0 
            housing_amount = (
                float(self.basic_salary)             
                                        * float(percent_cal)
                                                                / 100)
            self.housing_amount = housing_amount
            return housing_amount 
       
    @frappe.whitelist()        
    def salary_calculation(self):
        comp_list = self.get_components_and_amounts()
        salaries = self.salaries_amount(comp_list)       
        for k ,v in salaries.items():
            setattr(self, k, v)
        return salaries
         
        
    def get_components_and_amounts(self):
        if self.employee:
            if self.company:
                if not self.basic_salary or self.basic_salary < 0:
                    frappe.throw("Calculation cannot be performed without a set Basic Salary for the Employee: {emp}."
                                 .format(emp = self.employee),
                                 title=frappe._("Missing Basic Salary"))
                    return 
                employee_componets = list()
                if not  self.basic_salary_component: 
                    frappe.throw("Calculation cannot be performed without a Defined Basic Salary Component for the Employee: {emp}."
                                .format(emp = self.employee),
                                title=frappe._("Missing Basic Salary"))
                    return 
                employee_componets.append( 
                                frappe._dict(
                                        {'sal_comp' : self.basic_salary_component , 
                                         'amount' : self.basic_salary
                                        }
                                )
                )
                if self.is_housing_applicable:
                    if not self.housing_component:
                        frappe.throw(
                            "Please set the Salary Component for Housing to proceed with calculations for the employee: {emp}."
                            .format(emp = self.employee),
                            title =frappe._("Missing Housing Component")
                        )
                        return
                    self.check_housing()
                    if self.housing_amount <= 0 :
                        frappe.throw(
                            "The housing amount cannot be zero. Please verify the information.",
                            title = frappe._("Zero Housing Amount")
                        )
                        return 
                    
                    employee_componets.append(
                        frappe._dict(
                            {
                                'sal_comp' : self.housing_component,
                                'amount' : self.housing_amount
                            }
                        )
                    )
                if self.is_ss_applicable:
                    if not self.ss_component:
                        frappe.throw(
                            "Please Set Salary Component for Social Security to proceed with calculations for the employee: {emp}."
                            .format(emp = self.employee),
                            title = frappe._("Missing Salary Component")
                        )
                    employee_componets.append(
                        frappe._dict(
                            {
                                'sal_comp' : self.ss_component,
                                'amount' : self.ss_amount
                            }
                        )
                    )
                if self.other_salary_component:
                    if len(self.esc_table) != 0:
                        for esc in self.esc_table:
                            if not esc.salary_component:
                                frappe.throw(
                                    "In row {idx}, please set the salary component."
                                    .format(idx = esc.idx),
                                    title = frappe._("Missing Salary Component")
                                    )
                                return
                            if not esc.amount:
                                frappe.throw(
                                    "Calculation cannot continue without a set amount in row {idx} for salary component {sal_comp}."
                                    .format(idx = esc.idx , sal_comp = esc.salary_component))
                            employee_componets.append(
                                frappe._dict(
                                    {
                                        'sal_comp' : esc.salary_component,
                                        'amount' : esc.amount
                                    }
                                )
                            )
                            
                    else:
                        frappe.throw(
                            "Employee Salary Component Table Must include Salary Component"
                        )
                    
                return employee_componets
            else:
                frappe.throw(  
                            "Calculation cannot be performed without a specified company for employee {emp}."
                            .format(emp = self.company) ,
                            title = frappe._("Missing Company")
                            )
        else:
            frappe.throw("Cannot Calculate without set Employee." , 
                         title = frappe._("Missing Employee")
                         )         
            
    def salaries_amount(self , comp_list):
        basic_sal_comp = self.get_basic_salary_component()
        deduction_salary = 0 
        salary_with_allowance = 0 
        ss_salary = 0 
        eos_salary = 0
        for sal in comp_list:
            if basic_sal_comp == sal.sal_comp:
                deduction_salary += sal.amount
                salary_with_allowance+= sal.amount
                ss_salary+= sal.amount
                eos_salary+= sal.amount
            else:
                comp_doc = frappe.get_doc('Salary Component' , sal.sal_comp)
                if comp_doc.type == 'Earning':
                    if comp_doc.custom_is_overtime_applicable:
                        salary_with_allowance+= sal.amount
                    if comp_doc.custom_is_eos_applicable:
                        eos_salary+= sal.amount
                    if comp_doc.custom_is_ss_applicable:
                        ss_salary+= sal.amount
                    if comp_doc.custom_is_short_leave_applicable:
                        deduction_salary += sal.amount
        return {
            'deduction_salary':deduction_salary , 
            'basic_salary_with_allowance':salary_with_allowance,
            'ss_salary': ss_salary,
            'eos_salary':eos_salary
        }
        
    def validate(self):
        self.check_ss_numbers_length()
        self.check_housing()  
                  
    def check_housing(self):
        if self.is_housing_applicable:
            if (self.by_percent + self.by_amount) != 1:
                frappe.throw("Please Select an option for Housing, Either By Percentage or By Amount.", 
                             title= frappe._("Missing Housing Option")
                )
                if self.by_percent: 
                        emp_doc = frappe.get_doc('Employee' , self.employee)
                        emp_status = emp_doc.marital_status
                        if  not emp_status:
                            frappe.throw("Marital Status For Employee is Mandatory to Continue Calculations.")
                        
                        
                
    def check_ss_numbers_length(self):
        if self.is_ss_applicable:
            if len(str(self.ss_number)) != 9:
                frappe.throw("Social Security Number Must be nine digits." ,  
                                title=frappe._("Error Social Security Number") 
                    )
    
    def on_submit(self):
        self.check_escm_exists_date()
        self.check_amounts()
        self.ckeck_components()
        self.add_history_data()
        self.effect_in_employee()
        
    def check_escm_exists_date(self):
        exist_escm = frappe.db.sql("""
                                SELECT 
                                    name , from_date
                                FROM 
                                    `tabEmployee Salary Component Management` tescm 
                                WHERE 
                                    from_date >= %s 
                                    AND employee = %s 
                                    AND docstatus =1  
                                    AND name != %s
        """  , (self.from_date , self.employee , self.name) , as_dict = True)
        if len(exist_escm) != 0 :
            frappe.throw(
                """
                This employee already has <b>{name}</b> from date <b>{date}</b>. <br> 
                Start date cannot be earlier than that.
                """
                .format(emp = self.employee , name = exist_escm[0]['name'] , date = str(exist_escm[0]['from_date'])),
                title = frappe._("Exist ESCM")
                )
            
    def check_amounts(self):
        if not self.basic_salary or self.basic_salary <= 0:
            frappe.throw(
                "Basic salary cannot be zero. Please check and recalculate." , 
                title = frappe._("Validation Error")
            )
        if self.is_ss_applicable and self.ss_amount <=0:
           frappe.throw(
               "Social Security amount cannot be zero. Please check and recalculate." , 
               title = frappe._("Validation Error")
            )
        if self.is_housing_applicable and self.housing_amount <= 0:
            frappe.throw(
                "Housing amount cannot be zero. Please check and recalculate." , 
                title = frappe._("Validation Error")
            )
        if self.is_overtime_applicable and self.basic_salary_with_allowance <= 0:
            frappe.throw(
                "Basic Salary with Allowance cannot be zero. Please check and recalculate." , 
                title = frappe._("Validation Error")
            )
        if self.is_end_of_service_applicable and self.eos_salary <=0:
            frappe.throw(
                "End of Service Salary cannot be zero. Please check and recalculate." , 
                title = frappe._("Validation Error")
            )
            
    def ckeck_components(self):
        out_components = list()
        if self.is_ss_applicable:
            out_components.append(self.ss_component)
        if self.is_housing_applicable:
            out_components.append(self.housing_component)
        if self.other_salary_component:
            for esc in self.esc_table:
                if esc.salary_component in out_components:
                    frappe.throw("Salary Component <b>{comp}</b> Cant Be in Table and in Housing/ Social Security at the Same Time."
                                 .format(comp = esc.salary_component),
                                 title = frappe._("Validation Error")
                    )
    def define_html_component(self):
        style = """
                    <style>
                .wide-table { width: 100%; }
                .first-column { width: 60%;}
                .text-right {text-align: right; }
            </style>
        """
        html = """  <div class="container mt-3">"""
        html+= """      <table class="table table-bordered table-hover wide-table">"""
        html+= """          <thead class="thead-light"> """
        html+= """              <tr> """
        html+= """                  <th scope="col" class="first-column">Salary Component</th>"""
        html+= """                  <th scope="col" class="text-right">Amount</th> """
        html+= """              </tr> """ 
        html+= """          </thead> """
        html += "           <tbody>"
        for sal in self.esc_table:
            html += "           <tr>"
            html += f"              <td>{sal.salary_component}</td>"
            html += f"""            <td class="text-right">{sal.amount}</td> """
            html += "           </tr>"
        html += "           </tbody>"
        html += """     </table>
                    </div>"""
        code = style + html
        return code 
    
    def add_history_data(self):
        history_doc = self.add_esch_table()
        self.add_salary_component_history(history_doc)
        
        
    def add_esch_table(self):
        exist_emp = frappe.db.sql("""
                SELECT 
                    name 
                FROM 
                    `tabEmployee Salary Component History` tesch 
                WHERE 
                    employee = %s 
        """ , (self.employee) , as_dict = True )
        if len(exist_emp) != 0:
            history_doc = frappe.get_doc('Employee Salary Component History' , exist_emp[0]['name'])
        else:
            history_doc = frappe.new_doc('Employee Salary Component History')
            history_doc.employee = self.employee
            history_doc.employee_name = self.employee_name 
            history_doc.company = self.company
            history_doc.nationality = self.nationality
        
        for row in history_doc.esch_table  : 
            row.is_active = 0     
        html = self.define_html_component()
        data= frappe._dict({
                "is_active" : 1,
                "from_date" : self.from_date, 
                "escm_ref" : self.name,
                "edit_info" : self.edit_info, 
                "ss_start_date" : self.ss_start_date, 
                "basic_salary_component": self.basic_salary_component,
                "basic_salary" : self.basic_salary,
                "is_ss_applicable" : self.is_ss_applicable,
                "ss_component" : self.ss_component,
                "ss_number" : self.ss_number,
                "default_ss" : self.default_ss,
                "emp_ss_rate" : self.emp_ss_rate,
                "comp_ss_rate" : self.comp_ss_rate,
                "is_overtime_applicable" : self.is_overtime_applicable,
                "is_end_of_service_applicable" : self.is_end_of_service_applicable,
                "eos_default_period" :self.eos_default_period,
                "end_of_service_rate":self.end_of_service_rate,
                "is_housing_applicable" : self.is_housing_applicable,
                "housing_component" : self.housing_component,
                "by_percent" : self.by_percent,
                "by_amount" : self.by_amount,
                "default_percent" : self.default_percent,
                "percentage" : self.percentage,
                "housing_amount": self.housing_amount,
                "other_salary_component" : self.other_salary_component,
                "editor" : html,
                "deduction_salary" : self.deduction_salary,
                "edit_ss_salary" : self.edit_ss_salary,
                "ss_salary" : self.ss_salary,
                "ss_amount" : self.ss_amount,
                "basic_salary_with_allowance" : self.basic_salary_with_allowance,
                "eos_salary" : self.eos_salary
        })
        history_doc.append('esch_table' , data)
        history_doc.save()
        return history_doc
    
    
    def add_salary_component_history( self , history_doc):
        components = self.get_components_and_amounts()
        for row in history_doc.sal_comp_table  : 
            row.is_active = 0 
        for component in components:
            data = frappe._dict({
                'salary_component' : component.sal_comp,
                'amount' : component.amount,
                'is_active': 1 ,
                'from_date' : self.from_date ,
                'escm_ref' : self.name                    
            })
            history_doc.append('sal_comp_table' , data)
        history_doc.save()
        
    def effect_in_employee(self):
        emp_doc = frappe.get_doc('Employee' , self.employee)
        ### Overtime
        emp_doc.is_overtime_applicable = self.is_overtime_applicable
        
        ### EOS         
        emp_doc.custom_is_eos_applicable = self.is_end_of_service_applicable
        emp_doc.custom_eos_default_period = self.eos_default_period
        if  self.end_of_service_rate:
            emp_doc.custom_end_of_service_rate = self.end_of_service_rate     
        ### Social Security 
        emp_doc.custom_is_social_security_applicable = self.is_ss_applicable
        if  self.is_ss_applicable:
            emp_doc.custom_ss_number = self.ss_number
            emp_doc.custom_ss_start_date = self.ss_start_date
            emp_doc.custom_ss_salary = self.ss_salary
            emp_doc.custom_ss_amount = self.ss_amount
        ### Housing             
        emp_doc.custom_is_housing_applicable  = self.is_housing_applicable 
        if  self.is_housing_applicable :
            emp_doc.custom_by_percent = self.by_percent
            emp_doc.custom_by_amount = self.by_amount
            if self.by_amount:
                emp_doc.custom_housing_amount = self.housing_amount
            elif self.by_percent:
                emp_doc.custom_housing_percent = self.percentage
                emp_doc.custom_housing_amount = self.housing_amount 
        
        ### Salaries
        emp_doc.custom_basic_salary = self.basic_salary
        emp_doc.custom_salary_deduction = self.deduction_salary
        emp_doc.custom_basic_salary_with_allowance = self.basic_salary_with_allowance
        emp_doc.custom_eos_salary = self.eos_salary
        emp_doc.custom_employee_salary_component = []
        #### Salary Component
        components = self.get_components_and_amounts()
        for component in components : 
            emp_doc.append('custom_employee_salary_component' , 
                    {
                'salary_component':component.sal_comp,
                'is_active':1,
                'esc_amount':component.amount,
                'date':self.from_date
                }
            )
        emp_doc.custom_escm_ref = self.name
        emp_doc.save()