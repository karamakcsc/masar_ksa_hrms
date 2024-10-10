# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe  import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_date_in_priod , eos_provision
class EndofServiceCalculator(Document):
    
	@frappe.whitelist()
	def calculate_eos(self):
		if self.eos_salary <= 0:
			frappe.throw(
       				"The End of Service Salary must be greater than zero.", 
           			title=_("End of Service Salary")
              	)
			return
		if not self.from_date:
			frappe.throw(
				_("Date of Joining in Employee : {emp} Not Define , Please set it. "
      			.format(emp = self.employee)),
				title = _("Missing Date of Joining")
			)
		if not self.to_date:
			frappe.throw(
       			"The 'To Date' field is mandatory for executing the calculations.", 
          		title=_("Mandatory Fields")
            )
			return 

		if self.to_date < self.from_date:
			frappe.throw(
       			"The 'To Date' must be later than the 'From Date' to proceed with the calculations.", 
          		title=_("Mandatory Fields")
            )
			return 

		if not self.termination_type:
			frappe.throw("The 'Termination Type' is mandatory to proceed with the calculations.",
                title=_("Mandatory Fields")
            )
			return 
		if not self.employee:
			frappe.throw("The 'Employee' is mandatory to proceed with the calculations.",
                title=_("Mandatory Fields")
            )
			return 
		emp_doc = frappe.get_doc('Employee' , self.employee)
		if not emp_doc.company:
			frappe.throw("The 'Company' in Employee is mandatory to proceed with the calculations.",
                title=_("Mandatory Fields")
            )
			return 
		comp_doc = frappe.get_doc ('Company' , emp_doc.company )
		if self.eos_default_period:
			from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation
			eos_validation(comp_doc ,table_name = 'custom_comp_eos_table' , rate_name = 'salary_rate')
			periods_table = comp_doc.custom_comp_eos_table
		if not self.eos_default_period:
			if not self.end_of_service_rate:
				frappe.throw("The 'End of Service Rate' is mandatory to proceed with the calculations.",
                title=_("Mandatory Fields")
            	)
				return 
			elif self.end_of_service_rate:
				eos_rate = frappe.get_doc('End of Service Rate' , self.end_of_service_rate )
				periods_table = eos_rate.eos_table
		(period_days , 
			years, 
				months, 
					days , 
						num_days_in_year) = eos_date_in_priod(emp_doc.company, str(self.from_date) , str(self.to_date))
		self.working_days = period_days
		self.years = years
		self.months = months 
		self.days = days
		total_amount , year_amount , month_amount , day_amount = (
			eos_provision(data = frappe._dict(
				{
					'salary': self.eos_salary , 
					'years' : years,
					'months' : months,
					'days':days,
					'num_days_in_year': num_days_in_year,
					'termination_name':  self.termination_type,
					'periods_table' : periods_table
				}
			)
		))
		self.years_amount =year_amount
		self.months_amount = month_amount
		self.day_amount = day_amount
		self.total_amount = total_amount