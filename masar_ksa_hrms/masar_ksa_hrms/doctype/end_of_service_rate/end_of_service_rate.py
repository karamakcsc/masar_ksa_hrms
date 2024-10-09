# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation


class EndofServiceRate(Document):
	def validate(self):
		eos_validation(self, table_name = 'eos_table', rate_name = 'salary_rate')
