import frappe
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import group_by , eos_date_in_priod , eos_provision
from frappe.query_builder.functions import Coalesce, Sum , Max
        
        
        
        
        
        
        
def department_validation(self):
        d = frappe.qb.DocType('Department')
        exist_non_default_department = (
                frappe.qb.from_(d).select(d.name).where(d.custom_eos_default_account == 0 or d.custom_ss_default_account == 0 )
        ).run(as_dict = True)
        if len(exist_non_default_department) !=0: 
             for e in self.employees:
                     if e.employee and (e.department is None):
                            frappe.throw(
                                        _("The Department for Employee {0} is Mandatory.").format(e.employee)
                                )
                                                        
def company_journal_entry(self):
        """
		Create a Journal Entry for the given payroll entry (Company Jouranl Entry).
        """
        group = group_by()
        (       
                rate_condition , 
                expenses , 
                liabilities , 
                cost_center
        ) = company_rate_and_accounts(self = self)
        rows = (
                rows_ss_query(self = self, 
                condition = rate_condition, 
                group_by =group )
        )
        create_company_journal_entry(
                self=self , 
                cost_center=cost_center,
                rows=rows,
                group= group
                )
def get_defualt_department(self):
        d = frappe.qb.DocType('Department')
        d_sql = frappe.qb.from_(d).select(d.name).where(d.name.isin([e.department for e in self.employees]))
        eos_sql = d_sql.where(d.custom_eos_default_account == 1).run(as_dict = True)
        ss_sql = d_sql.where(d.custom_ss_default_account == 1 ).run(as_dict = True )
        eos_mandetory = True if len(eos_sql) != 0 else False 
        ss_mandetoary  =  True if len(ss_sql) != 0 else False 
        return { 'eos' : eos_mandetory , 'ss' : ss_mandetoary}
        
def company_rate_and_accounts(self):
        mandetory = get_defualt_department(self=self)
        condition = list()
        company_doc = frappe.get_doc('Company' , self.company)
        expenses = company_doc.custom_ss_expenses

        liabilities = company_doc.custom_ss_liabilities
        #### Mandetory 
        if (mandetory['ss'] == True) and ((expenses is None) or (liabilities is None)): 
                frappe.throw(
                        _("""
                        Some departments have a default value set. 
                        Please ensure that there are corresponding expense and liability accounts for social security."""
                        )
                )

        sa_rate = company_doc.custom_comp_ss_sa_rate

        if sa_rate == 0 :
                """ Add Condition """
                condition.append(
                        'sa'
                ) 
                
        other_rate = company_doc.custom_comp_ss_other_rate

        if other_rate == 0 :
                """ Add Condition """
                condition.append(
                        'other'
                ) 
        if self.cost_center:
                
               cost_center = self.cost_center
        else:
                
               cost_center= company_doc.cost_center
               
        return condition , expenses , liabilities , cost_center
   
def create_company_journal_entry(
                self , 
                cost_center,
                rows,
                group
        ):
        jv = frappe.new_doc('Journal Entry')
        jv.posting_date = self.posting_date
        jv.company = self.company
        jv.cost_center = cost_center
        jv.user_remark = f"Payroll Entry is:{self.name} in the Posting Date :{self.posting_date} for Company Social Security."
        if len(rows) !=0 : 
                for r in rows:
                        if float(r.salary_amount):
                                account = jv.append('accounts' , {})
                                account.account = r.ss_liabilities
                                account.credit_in_account_currency = float(r.salary_amount)
                                account.cost_center = r.ss_cost_center
                                if group == 'Employee':
                                        account.party_type = group
                                        account.party = r.employee
                                account.reference_type = self.doctype
                                account.reference_name = self.name
                                account.reference_due_date = self.posting_date
                                account.user_remark = f"""reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company Social Security.
                                        """
                                debit_account = jv.append('accounts' , {})
                                debit_account.account = r.ss_expenses
                                debit_account.debit_in_account_currency = float(r.salary_amount)
                                debit_account.cost_center = r.ss_cost_center
                                debit_account.reference_type = self.doctype
                                debit_account.reference_name = self.name
                                debit_account.reference_due_date = self.posting_date    
                                debit_account.user_remark = f"""reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company Social Security.
                                        """
                        else:
                                frappe.msgprint(
                                        _(f"Employee {r.employee} has no Social Security in the Salary Structure."),
                                        alert=True,
                                        indicator="blue",
			        )
                        
                jv.save(ignore_permissions=True)
                jv.submit()
        else:
                frappe.msgprint(
                                _("There is no employee with Social Security. Company Journal Entry not created."),
                                alert=True,
                                indicator="blue",
                        )
def rows_ss_query(self, condition, group_by):
        employees_in_table = [emp.employee for emp in self.employees]
        e = frappe.qb.DocType("Employee")
        d = frappe.qb.DocType("Department")
        c = frappe.qb.DocType("Company")
        employees = (
                frappe.qb.from_(e)
                .left_join(d)
                .on(d.name == e.department)
                .left_join(c)
                .on(c.name == e.company)
                .select(
                        (
                               (e.name)
                               .as_("employee")
                        ),
                        (
                                (d.name)
                                .as_('department')
                        ),
                        ((
                                Sum(
                                        frappe.qb.terms.Case()
                                                .when(
                                                        (e.custom_nationality == "Saudi Arabia"),
                                                        (e.custom_ss_salary * c.custom_comp_ss_sa_rate / 100)
                                                ).else_(
                                                        (e.custom_ss_salary * c.custom_comp_ss_other_rate / 100)
                                                )
                                )).as_("salary_amount")
                        ),
                        (
                                (
                                        frappe.qb.terms.Case()
                                        .when(
                                                (d.custom_ss_default_account == 0 ), 
                                                (d.custom_ss_expenses)
                                        )
                                        .else_(
                                               (c.custom_ss_expenses ) 
                                        )
                                ).as_('ss_expenses')
                        ),
                        (
                                (
                                        frappe.qb.terms.Case()
                                        .when(
                                                (d.custom_ss_default_account == 0 ), 
                                                (d.custom_ss_liabilities)
                                        )
                                        .else_(
                                               (c.custom_ss_liabilities ) 
                                        )
                                ).as_('ss_liabilities')
                        ),
                        (   
                                Coalesce(
                                        d.custom_ss_cost_center, 
                                        d.payroll_cost_center, 
                                        e.payroll_cost_center, 
                                        c.cost_center
                                )
                                .as_("ss_cost_center")
                        ),
                ) 
                .where(e.custom_is_social_security_applicable == 1)
                .where(e.status == "Active")
                .where(e.name.isin(employees_in_table))
                .groupby(
                        (
                                frappe.qb.terms.Case()
                                        .when(d.custom_ss_default_account == 0, d.custom_ss_expenses)
                                        .else_(c.custom_ss_expenses)
                        ),
                        
                        (
                                frappe.qb.terms.Case()
                                        .when(d.custom_ss_default_account == 0, d.custom_ss_liabilities)
                                        .else_(c.custom_ss_liabilities)
                        ),
                        (
                                Coalesce(
                                        d.custom_ss_cost_center, 
                                        d.payroll_cost_center, 
                                        e.payroll_cost_center, 
                                        c.cost_center
                                        )
                        )
                )                
        )
        if len(condition) != 0 :
                if 'sa' in condition:
                        employees = (
                                employees
                                .where(
                                                e.custom_nationality != 'Saudi Arabia'    
                                        )
                                )
                if 'other' in condition:
                        employees = (
                                employees
                                .where(
                                                e.custom_nationality == 'Saudi Arabia'
                                )
                        )
        if group_by == 'Employee':
                employees = employees.groupby(e.name)
        return employees.run(as_dict=True)


def eos_provision_and_jv(self):
        rows = (
        create_eos_peroision(self)
        )

        jv_name = (create_eos_jv(
                self , 
                rows)
        )
        (add_jv_nameto_eosp(
                rows , 
                jv_name)
        )
      

def company_eos_accounts( self , company_name):
        company = frappe.get_doc('Company' , company_name)
        mandetory = get_defualt_department(self=self)
        if (
                mandetory['eos'] == True  
                and 
                (
                ( company.custom_end_of_service_expenses is None)
                or 
                ( company.custom_end_of_service_liabilities is None )
                )):
                    frappe.throw( 
                                 _(
                        """
                        Some departments have a default value set. 
                        Please ensure that there are corresponding expense and liability accounts for End od Service.
                        """
                        )
                )
        return company.custom_end_of_service_expenses , company.custom_end_of_service_liabilities


def previous_provision_value(eosp):
    pd = frappe.qb.DocType("EOS Provision Details")
    subquery = (((
        frappe.qb.from_(pd)
                .select(Max(pd.idx))
                .where(
                        pd.parent == eosp.name
                )
    ).run())
    [0][0]
    )
    sql = (
        frappe.qb.from_(pd)
        .select(pd.provision)
        .where(pd.parent == eosp.name)
        .where(pd.idx == subquery)
    ).run()
    return sql[0][0] if sql else 0

def create_eos_peroision(self):
        date = frappe._dict({
                'posting_date' : self.posting_date , 
                'start_date' : self.start_date , 
                'end_date' : self.end_date
        })
        rows_list = list()
        for employee in self.employees:
                (
                        expenses , 
                        liabilities , 
                        cost_center 
                ) = get_accounts_and_cost_center_for_emmployee(employee = employee.employee)
                data = frappe._dict({
                        'employee' : employee.employee , 
                        'employee_name' : employee.employee_name , 
                        'company' : self.company , 
                        'department' : employee.department ,
                        'cost_center' : cost_center, 
                        'expenses' : expenses, 
                        'liabilities' : liabilities
                })
                rows = create_emp_eos_peroision(date , data)
                rows_list.append(rows)
        return rows_list




def get_accounts_and_cost_center_for_emmployee(employee = None):
        if employee:
                e = frappe.qb.DocType('Employee')
                d = frappe.qb.DocType('Department')
                c = frappe.qb.DocType('Company')
                sql = (
                        frappe.qb.from_(e)
                        .left_join(d)
                        .on(d.name == e.department)
                        .left_join(c)
                        .on(c.name == e.company)
                        .select(
                                (
                                        (
                                                frappe.qb.terms.Case()
                                                .when(
                                                        (d.custom_ss_default_account == 0 ), 
                                                        (d.custom_ss_expenses)
                                                )
                                                .else_(
                                                (c.custom_ss_expenses ) 
                                                )
                                        ).as_('expenses')
                                ),
                                (
                                        (
                                                frappe.qb.terms.Case()
                                                .when(
                                                        (d.custom_ss_default_account == 0 ), 
                                                        (d.custom_ss_liabilities)
                                                )
                                                .else_(
                                                (c.custom_ss_liabilities ) 
                                                )
                                        ).as_('liabilities')
                                ),
                                (   
                                        Coalesce(
                                                d.custom_ss_cost_center, 
                                                d.payroll_cost_center, 
                                                e.payroll_cost_center, 
                                                c.cost_center
                                        )
                                        .as_("cost_center")
                                )
                        )
                        .where( e.name == employee )
                ).run(as_dict = True)
                if sql and sql[0] and (sql[0]['expenses'] or sql[0]['liabilities'] or sql[0]['cost_center']): 
                        return sql[0]['expenses'] , sql[0]['liabilities'] , sql[0]['cost_center']
        return None , None , None 

def create_emp_eos_peroision(date , data):
        emp_doc = frappe.get_doc('Employee' , data.employee)
        if emp_doc.custom_eos_default_period:
                company_doc = frappe.get_doc('Company' , emp_doc.company)
                periods_table = company_doc.custom_comp_eos_table
        else:
                if emp_doc.custom_end_of_service_rate:
                        eos_rate = frappe.get_doc('End of Service Rate' ,  emp_doc.custom_end_of_service_rate)
                        periods_table = eos_rate.eos_table
                else:
                        frappe.throw('Employee {emp} must has End of Service Rate or get EOS Defualt.'.format(emp=emp_doc.name))

        if frappe.db.exists('End of Service Provision' , data.employee):
                eosp = frappe.get_doc('End of Service Provision' , data.employee)
        else:
                eosp = frappe.new_doc('End of Service Provision')
                eosp.employee = data.employee
                eosp.employee_name = data.employee_name
                eosp.company = data.company
                eosp.department = data.department
        (       period_days , 
                years, 
		months, 
                days , 
		num_days_in_year
        ) = eos_date_in_priod( data.company , str(emp_doc.date_of_joining) , str(date.end_date))
        (total_amount , 
         year_amount , 
         month_amount , 
         day_amount
        )       =       (
			eos_provision(data =( 
                                frappe._dict(
				{
					'salary': float(emp_doc.custom_eos_salary) , 
					'years' : years,
					'months' : months,
					'days':days,
					'num_days_in_year': num_days_in_year,
					'termination_name':  None,
					'periods_table' : periods_table
				}
			)
		))
        )
        row = frappe._dict(
                        {
                     'posting_date' : date.posting_date,
                     'eos_salary' : float(emp_doc.custom_eos_salary), 
                     'from_date' : date.start_date, 
                     'to_date': date.end_date, 
                     'working_day': period_days , 
                     'years' : years , 
                     'months' : months, 
                     'days ': days , 
                     'years_amount' : year_amount,
                     'months_amount' : month_amount,
                     'days_amount' : day_amount, 
                     'total_amount' : round(total_amount , 3), 
                     'provision' : round(total_amount , 3) 
                })
        if len(eosp.provisions) == 0:
                row['pervious_provision'] = 0
                row['provision_diff'] = round(total_amount , 3)
                return_amount = round(total_amount , 3)
        else: 
                pervious_provision = float(previous_provision_value(eosp))
                row['pervious_provision'] = pervious_provision
                row['provision_diff'] = round((total_amount - pervious_provision) ,3)
                return_amount = round((total_amount - pervious_provision) ,3)
        row_added = eosp.append('provisions' , row)
        eosp.total_amount= round(total_amount , 3)
        eosp.run_method('save')
        dict_to_return = frappe._dict({
                'ch_name' : row_added.name,
                'employee' : data.employee,
                'amount' : round(return_amount , 3),
                'cost_center' : data.cost_center, 
                'expenses' : data.expenses, 
                'liabilities' : data.liabilities 
        })
        return dict_to_return



def create_eos_jv(self , rows):
        default_expenses , default_liabilities =  company_eos_accounts(self , self.company) 
        debit_lst = list()
        jv = frappe.new_doc('Journal Entry')
        jv.posting_date = self.posting_date
        jv.company = self.company 
        jv.user_remark = f"Payroll Entry is:{self.name} in the Posting Date :{self.posting_date} for Company End of Service."
        for c in rows:
                if c.amount != 0 : 
                        
                        """
                                Credit for Employee End of Service (Company Amount).
                                
                                "The End of Service value is calculated for eash employee to be allocated to employee and 

                                deducted from the company account."

                        """
                        cr_amount = round(c.amount , 2 )
                        debit_lst = debit_accounts_and_amounts_for_eos(
                                debit_lst=debit_lst,
                                new_amount=cr_amount,
                                new_account=c.expenses,
                                new_cost_center=c.cost_center
                        )
                        cr_account = jv.append('accounts' , {})
                        cr_account.account = c.liabilities
                        cr_account.credit_in_account_currency = cr_amount
                        cr_account.cost_center = c.cost_center
                        cr_account.party_type = "Employee"
                        cr_account.party =  c.employee
                        cr_account.reference_type = self.doctype
                        cr_account.reference_name = self.name
                        cr_account.reference_due_date = self.posting_date
                        cr_account.user_remark = f"""
                        Reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company End of Service.
                                        """
        if len(debit_lst) != 0 : 
                for d in debit_lst:
                        d = frappe._dict(d)
                        expenses , cost_center  = (d.key)[0] , (d.key)[1] 
                        if d.amount != 0 :
                                dr_account = jv.append('accounts' , {})
                                dr_account.account = expenses
                                dr_account.debit_in_account_currency = d.amount
                                dr_account.cost_center = cost_center
                                dr_account.reference_type = self.doctype
                                dr_account.reference_name = self.name
                                dr_account.reference_due_date = self.posting_date
                                dr_account.user_remark = f"""
                Reference Type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company End of Service.
                                                """ 
        
        jv.save(ignore_permissions=True)
        jv.submit()                                               
        return jv.name



def debit_accounts_and_amounts_for_eos(
                debit_lst = None, 
                new_amount = 0.0, 
                new_account = None , 
                new_cost_center = None

        ):
                
                if debit_lst is None:
                        debit_lst = []
                key = (new_account , new_cost_center)
                value = 'amount'
                if len(debit_lst) == 0:
                        debit_lst.append({
                                'key' : key,
                                value : new_amount
                        })
                else: 
                        key_exists = False
                        for d  in debit_lst:
                                if key == d['key']: 
                                        d[value] += new_amount
                                        key_exists = True
                                        break
                        if not key_exists:
                                debit_lst.append({
                                'key': key,
                                'amount' : new_amount
                        })
                return debit_lst

def add_jv_nameto_eosp(rows , jv_name):
        for row in rows:

                frappe.db.set_value('EOS Provision Details' , row.ch_name , 'ref_jv' , jv_name)
                frappe.db.commit()