import frappe
from frappe import _
import datetime
from datetime import timedelta , datetime , date
from datetime import datetime
from dateutil.relativedelta import relativedelta

def period_validate(self):
        data = frappe.db.sql('''
        SELECT 
            name 
        FROM 
            `tab{doc}`
        WHERE 
            employee = %s AND 
            posting_date BETWEEN %s AND %s AND 
            docstatus = 1 AND
            name != %s
        '''
            .format(doc = self.doctype), 
            (self.employee, self.from_date, self.to_date , self.name)
        )
        return data

def date_period(self):
        try:
            if self.posting_date:
                posting_date = datetime.strptime(self.posting_date, '%Y-%m-%d').date()
                start_month = posting_date.replace(day=1)
                next_month = start_month.replace(day=28) + timedelta(days=4) 
                end_month = next_month - timedelta(days=next_month.day)
                self.from_date = start_month
                self.to_date = end_month
                return {
                    'from_date': start_month, 
                    'to_date' : end_month
				} 
            else : 
                self.from_date = None
                self.to_date = None
                return 1 
        except Exception as ex:
            frappe.throw(f'Error While Execute Get Date Period: {str(ex)}')
            
            
def create_additional_salary(data):
        additional_salary = frappe.new_doc('Additional Salary')
        additional_salary.employee = data.employee
        additional_salary.employee_name = data.employee_name
        additional_salary.department = data.department
        additional_salary.company = data.company
        additional_salary.is_recurring = data.is_recurring
        additional_salary.payroll_date = data.payroll_date
        additional_salary.salary_component =  data.salary_component
        additional_salary.type  = data.type
        additional_salary.amount =  data.amount
        additional_salary.deduct_full_tax_on_selected_payroll_date =  (
            data.deduct_full_tax_on_selected_payroll_date)
        additional_salary.overwrite_salary_structure_amount = (
            data.overwrite_salary_structure_amount)
        additional_salary.ref_doctype = data.ref_doctype
        additional_salary.ref_docname = data.ref_docname
        additional_salary.insert(ignore_permissions=True)
        additional_salary.submit()
        return additional_salary
    
def eos_validation(self, table_name, rate_name):
    next_year = None
    last_row = len(getattr(self, table_name))
    
    for reg in getattr(self, table_name):
        
        rate = getattr(reg, rate_name)
        if rate > 100:
            frappe.throw(
                _("Rate cannot exceed 100. In Row {idx}"
                  .format(idx=reg.idx)
                  ), 
                title=_("Rate Error")
            )
        
        if reg.idx < last_row and reg.has_period and  reg.from_year >= reg.to_year:
            frappe.throw(
                _("The From Year in Row {idx} must be less than To Year."
                  .format(idx=reg.idx)
                  ), 
                title=_("Year Range Error")
            )
        
        if next_year is not None:
            if reg.from_year < next_year:
                frappe.throw(
                    _("The From Year in Row {idx} cannot be less than the To Year of the previous row (Row {previous_idx})."
                      .format(idx=reg.idx, previous_idx=reg.idx - 1)
                    ), 
                    title=_("Year Range Error")
                )
            elif reg.from_year > next_year:
                frappe.throw(
                    _("The From Year in Row {idx} must be equal to the To Year of the previous row (Row {previous_idx}). It should be {next_year}."
                      .format(idx=reg.idx, previous_idx=reg.idx - 1, next_year=next_year)
                    ), 
                    title=_("Year Range Error")
                )
        
        if reg.idx == last_row:
            if reg.has_period != 0:
                frappe.throw(
                    _("The Has Period in the last row must be set to 0."), 
                    title=_("Period Error")
                )
            if reg.to_year:
                frappe.throw(
                    _("The last row should not have a To Year value."), 
                    title=_("Year Error")
                )
        else:
            if reg.has_period != 1:
                frappe.throw(
                    _("All Rows Except the Last one Must Have Has Period set to 1. In Row {idx}"
                      .format(idx=reg.idx)), 
                    title=_("Period Error")
                )
            if not reg.to_year:
                frappe.throw(
                    _("All Rows with Has Period set to 1 must have a To Year value. In Row {idx}"
                      .format(idx=reg.idx)), 
                    title=_("Year Error")
                )    
        next_year = reg.to_year


def get_date_details(from_date_str , to_date_str):
    from_date = (
                datetime
                .strptime(str(from_date_str), '%Y-%m-%d')
                .date())
    to_date = (
                datetime
                .strptime(str(to_date_str), '%Y-%m-%d')
                .date())
    delta = relativedelta(to_date, from_date)
    years = delta.years
    months = delta.months
    days = delta.days +1
    return years, months, days   

def group_by():
        setting = frappe.get_doc('Payroll Settings')
        if setting.process_payroll_accounting_entry_based_on_employee == 1 :
                return 'Employee'
        elif setting.process_payroll_accounting_entry_based_on_employee == 0 :
                return 'Cost Center'

def eos_date_in_priod(company , from_date_str , to_date_str):
    company_doc = frappe.get_doc('company' , company)
    working_day_30 = company_doc.custom_working_day_30
    if working_day_30 == 1 :
        (total_days ,
        years, 
        months, 
        days
        ) = calculate_dates360(from_date_str, to_date_str)
        return total_days , years, months, days, 360 
    else: 
        (total_days , 
        years, 
        months, 
        days
        ) = calculate_all_days(from_date_str, to_date_str)
        return total_days , years, months, days, 365
def calculate_dates360(from_date_str, to_date_str):
    years ,months ,days = get_date_details(from_date_str , to_date_str)
    if days > 29:
        months += 1
        days = 0 
    if months == 12:
        years+=1
        months = 0
    total_days = years * 360 + months * 30 + days
    return total_days , years, months, days


def calculate_all_days(from_date_str, to_date_str):
    years ,months ,days = get_date_details(from_date_str , to_date_str)
    from_date = (
                datetime
                .strptime(str(from_date_str), '%Y-%m-%d')
                .date())
    to_date = (
                datetime
                .strptime(str(to_date_str), '%Y-%m-%d')
                .date())    
    total_days = (to_date - from_date).days + 1 
    return total_days , years, months, days

def eos_provision(data):
        salary = data.salary
        years = data.years
        months = data.months
        days = data.days
        num_days_in_year = data.num_days_in_year
        salary_in_day = salary / num_days_in_year
        termination_name = data.termination_name
        if termination_name is not None:
            termination_type = frappe.get_doc('Termination Type' , termination_name)
        else:
            termination_type = None
        periods_table = data.periods_table
        years_in_loop = years
        years_amount = 0 
        for period in periods_table:
            final_rate = period.salary_rate  / 100
            if period.has_period:
                if years_in_loop <= period.to_year:
                    years_amount += (   float(salary_in_day) * 
                                        float(num_days_in_year) * 
                                        float(years_in_loop) *  
                                        float(final_rate)
                                    )
                    break
                elif years_in_loop > period.to_year:
                    years_amount += (   float(salary_in_day) * 
                                        float(num_days_in_year) * 
                                        float(period.to_year - period.from_year) *  
                                        float(final_rate)
                                    )
            else:
                years_amount += (   float(salary_in_day) * 
                                    float(num_days_in_year) * 
                                    float(years_in_loop - period.from_year) *  
                                    float(final_rate)
                                )
        months_amount = (   float(salary_in_day) * 
                            30 * 
                            float(final_rate) * 
                            months
                        )
        days_amount = ( float(salary_in_day) * 
                        float(final_rate) * 
                        days
                    )   
        if  termination_type:
            if termination_type.is_resignation:
                    for resignation in termination_type.res_periods_table:
                        start_period = resignation.from_year
                        end_period = resignation.to_year
                        if resignation.has_period:
                            if(years_in_loop >= start_period and years_in_loop < end_period):
                                resignation_rate = resignation.rate /100
                                break
                        else:
                            if(years_in_loop >= start_period): 
                                resignation_rate = resignation.rate /100
                                break
            else:
                resignation_rate = 1  
        else:
            resignation_rate = 1 
        year_amount = (years_amount * 
                       resignation_rate)
        month_amount = (months_amount * 
                        resignation_rate)
        day_amount = (days_amount * 
                      resignation_rate)
        total_amount = ((days_amount + 
                        months_amount + 
                        years_amount) * resignation_rate
                        )
        return total_amount , year_amount , month_amount , day_amount



def daily():
        activate_shift()
        
def activate_shift():
        """
        New Day , the function will be execute to Active the toady shift type and deactive the yesterday shift 

        be check the shift for Employee Shift Management today Shift. 


            sa or tsa : Shift Assignment
            esa : Employee Shift Management or for custom field : custom_employee_shift_management
            esm : Employee Shift Management
        """
        current_date = datetime.now()
        today_name = current_date.weekday()
        today = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][today_name]
        day_shift_type = today.lower()+'_st' ######### today shift type 
        sa = frappe.qb.DocType('Shift Assignment')
        sa_sql = (
             frappe.qb.from_(sa)
             .select(
                  (sa.custom_employee_shift_management) , 
                  (sa.name),
                  (sa.shift_type)
             )
             .where(sa.docstatus ==1 )
        ).run(as_dict = True)
        esa_list = list()
        for sa_loop  in sa_sql:
                if (
                    sa_loop.custom_employee_shift_management is not None and 
                    sa_loop.custom_employee_shift_management not in esa_list
                    ):
                        esa_list.append(sa_loop.custom_employee_shift_management)
        esm = frappe.qb.DocType('Employee Shift Management')
        for esa in esa_list:
                
                esm_sql = ((
                    frappe.qb.from_(esm)
                    .select(
                        (esm.saturday_st),
                        (esm.sunday_st),
                        (esm.monday_st),
                        (esm.tuesday_st),
                        (esm.wednesday_st),
                        (esm.friday_st)
                    )
                    .where(esm.status == 'Active')
                    .where(esm.docstatus == 1)
                    .where(esm.name  == esa)
                )
                        .run(as_dict = True)
                )
                today_shift_type = esm_sql[0][day_shift_type]
                for tsa in sa_sql:
                    name = tsa.name
                    yestery_day_shift_type = tsa.shift_type
                    if today_shift_type is None:
                        status = 'Inactive'
                    elif today_shift_type != yestery_day_shift_type:
                        status = 'Inactive'
                    elif today_shift_type == yestery_day_shift_type:
                        status = 'Active'
                    frappe.db.set_value(sa,name,'status',status)
                    doc = frappe.get_doc(sa,name)
                    doc.status = status
                    doc.save()