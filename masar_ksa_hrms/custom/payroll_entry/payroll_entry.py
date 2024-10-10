import frappe
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import group_by , eos_date_in_priod , eos_provision
from frappe.query_builder.functions import Coalesce, Sum , Max
        
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
        ) = company_rate_and_accounts(self)
        employees = (
        employees_query(self, 
                condition = rate_condition, 
                group_by =group )
        )
        create_company_journal_entry(
                self , 
                expenses , 
                liabilities , 
                cost_center,
                employees,
                group)
        
def company_rate_and_accounts(self):
        condition = list()
        company_doc = frappe.get_doc('Company' , self.company)
        expenses = company_doc.custom_ss_expenses
        if not expenses:
                frappe.throw(
                        'Set Social Security Expenses Account for Company Journal Entry.',
                        title=_("Missing Soical Security Expenses")
                )
        liabilities = company_doc.custom_ss_liabilities
        if not liabilities:
                frappe.throw(
                        'Set Social Security Liabilities Account for Company Journal Entry.',
                        title=_("Missing Soical Security Liabilities")
                )      
        sa_rate = company_doc.custom_comp_ss_sa_rate
        if sa_rate is None:
                frappe.throw(
                        'Set Company Social Security Rate for Saudi Arabia for Company Journal Entry',
                        title = _("Missing Rate")
                )
        if sa_rate == 0 :
                """ Add Condition """
                condition.append(
                        'sa'
                ) 
        other_rate = company_doc.custom_comp_ss_other_rate
        if other_rate is None:
                frappe.throw(
                        'Set Company Social Security Rate for Saudi Arabia for Company Journal Entry',
                        title = _("Missing Rate")
                )
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
                expenses , 
                liabilities , 
                cost_center,
                employees,
                group
        ):
        debit_amount = 0 
        jv = frappe.new_doc('Journal Entry')
        jv.posting_date = self.posting_date
        jv.company = self.company
        jv.cost_center = cost_center
        jv.user_remark = f"Payroll Entry is:{self.name} in the Posting Date :{self.posting_date} for Company Social Security."
        for emp in employees:
                """
                Credit for Employees (Company Amount).
                """
                if float(emp.salary_amount):
                        debit_amount += float(emp.salary_amount)
                        account = jv.append('accounts' , {})
                        account.account = liabilities
                        account.credit_in_account_currency = float(emp.salary_amount)
                        account.cost_center = emp.payroll_cost_center
                        if group == 'Employee':
                                account.party_type = group
                                account.party = emp.name
                        account.reference_type = self.doctype
                        account.reference_name = self.name
                        account.reference_due_date = self.posting_date
                        account.user_remark = f"""reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company Social Security.
                                        """
                else:
                        frappe.msgprint(
                                        _(f"Employee {emp.name} has no Social Security in the Salary Structure."),
                                        alert=True,
                                        indicator="blue",
			)
        if debit_amount != 0 :
                debit_account = jv.append('accounts' , {})
                debit_account.account = expenses
                debit_account.debit_in_account_currency = (
                                        round(debit_amount , 3)
                                        )
                debit_account.cost_center = cost_center
                debit_account.reference_type = self.doctype
                debit_account.reference_name = self.name
                debit_account.reference_due_date = self.posting_date    
                debit_account.user_remark = f"""reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company Social Security.
                                        """
                jv.save(ignore_permissions=True)
                jv.submit()
        else:
                frappe.msgprint(
                                _("There is no employee with Social Security. Company Journal Entry not created."),
                                alert=True,
                                indicator="blue",
                        )
def employees_query(self, condition, group_by):
        employees_in_table = [emp.employee for emp in self.employees]
        employee = frappe.qb.DocType("Employee")
        department = frappe.qb.DocType("Department")
        company = frappe.qb.DocType("Company")
        employees = (
                frappe.qb.from_(employee)
                .select(
                        (
                                employee.name
                        ),
                        (   
                                Coalesce(employee.payroll_cost_center, department.payroll_cost_center)
                                .as_("payroll_cost_center")
                        ),
                        (
                        Sum(
                                frappe.qb.terms.Case()
                                        .when(
                                                (employee.custom_nationality == "Saudi Arabia"),
                                                (employee.custom_ss_salary * company.custom_comp_ss_sa_rate / 100)
                                        )
                                        .else_(
                                                (employee.custom_ss_salary * company.custom_comp_ss_other_rate / 100)
                                        )
                        )
                ).as_("salary_amount")
                
                )
                .join(department)
                
                .on(department.name == employee.department)
                
                .join(company)
                
                .on(company.name == employee.company)
                
                .where(employee.custom_is_social_security_applicable == 1)

                .where(employee.status == "Active")

                .where(employee.name.isin(employees_in_table))                
        )
        if len(condition) != 0 :
                if 'sa' in condition:
                        (
                                employees
                                .where(
                                                employee.custom_nationality != 'Saudi Arabia'    
                                        )
                                )
                if 'other' in condition:
                        (
                                employees
                                .where(
                                                employee.custom_nationality == 'Saudi Arabia'
                                )
                        )

        if group_by == 'Employee':

                employees.groupby(employee.name )
        else:
                employees.groupby(employee.payroll_cost_center)

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
      

def company_eos_accounts(company_name):
        company = frappe.get_doc('Company' , company_name)
        if not company.custom_end_of_service_expenses:
                frappe.throw(
                        'set End of Service Expneses Account in Company.'
                )
                return 
        if not company.custom_end_of_service_liabilities:
                frappe.throw(
                        'Set End of Service Liabilities Account in Company.'
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
                emp_doc = frappe.get_doc('Employee' , employee.employee) 
                data = frappe._dict({
                        'employee' : employee.employee , 
                        'employee_name' : employee.employee_name , 
                        'company' : self.company , 
                        'department' : employee.department ,
                        'cost_center' : emp_doc.payroll_cost_center
                })
                rows = create_emp_eos_peroision(date , data)
                rows_list.append(rows)
        return rows_list


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
        if len(eosp.perovisions) == 0:
                row['pervious_provision'] = 0
                row['provision_diff'] = round(total_amount , 3)
                return_amount = round(total_amount , 3)
        else: 
                pervious_provision = float(previous_provision_value(eosp))
                row['pervious_provision'] = pervious_provision
                row['provision_diff'] = round((total_amount - pervious_provision) ,3)
                return_amount = round((total_amount - pervious_provision) ,3)
        row_added = eosp.append('perovisions' , row)
        eosp.total_amount= round(total_amount , 3)
        eosp.run_method('save')
        dict_to_return = frappe._dict({
                'ch_name' : row_added.name,
                'employee' : data.employee,
                'amount' : round(return_amount , 3),
                'cost_center' : data.cost_center
        })
        return dict_to_return



def create_eos_jv(self , rows):
        expenses , liabilities =  company_eos_accounts(self.company) 
        c,e,l, cost_center = company_rate_and_accounts(self)
        debit_amount = 0 
        jv = frappe.new_doc('Journal Entry')
        jv.posting_date = self.posting_date
        jv.company = self.company 
        jv.cost_center = cost_center
        jv.user_remark = f"Payroll Entry is:{self.name} in the Posting Date :{self.posting_date} for Company End of Service."
        for row in rows:
                """
                        Credit for Employee End of Service (Company Amount).
                        
                        "The End of Service value is calculated for eash employee to be allocated to employee and 

                        deducted from the company account."

                """
                cr_amount = round(row.amount , 2 )
                debit_amount += cr_amount
                cr_account = jv.append('accounts' , {})
                cr_account.account = liabilities
                cr_account.credit_in_account_currency = cr_amount
                cr_account.cost_center = row.cost_center
                cr_account.party_type = "Employee"
                cr_account.party =  row.employee
                cr_account.reference_type = self.doctype
                cr_account.reference_name = self.name
                cr_account.reference_due_date = self.posting_date
                cr_account.user_remark = f"""Reference type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company End of Service.
                                        """
        if debit_amount !=0 :
                dr_account = jv.append('accounts' , {})
                dr_account.account = expenses
                dr_account.debit_in_account_currency = debit_amount
                dr_account.cost_center = cost_center
                dr_account.reference_type = self.doctype
                dr_account.reference_name = self.name
                dr_account.reference_due_date = self.posting_date
                dr_account.user_remark = f"""Reference Type is Payroll Entry , Reference Name is {self.name} and Reference Due Date is :{self.posting_date} for Company End of Service.
                                        """ 
                jv.save(ignore_permissions=True)
                jv.submit()                                               
        return jv.name

def add_jv_nameto_eosp(rows , jv_name):
        for row in rows:

                frappe.db.set_value('EOS Provision Details' , row.ch_name , 'ref_jv' , jv_name)
                frappe.db.commit()