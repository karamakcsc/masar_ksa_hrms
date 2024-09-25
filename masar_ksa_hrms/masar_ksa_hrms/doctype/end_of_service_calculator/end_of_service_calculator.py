# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe  import _
from datetime import datetime , timedelta
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import get_number_of_days_in_year
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

		termination_type = self.termination_type
		salary = self.eos_salary
		period_days , years, months, days = get_number_of_days_in_year(str(self.from_date) , str(self.to_date))
		self.working_days = period_days
		self.years = years
		self.months = months 
		self.days = days
