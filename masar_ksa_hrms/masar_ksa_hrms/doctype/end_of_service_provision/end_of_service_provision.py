# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EndofServiceProvision(Document):
	def on_change(self):
		self.cal_total_amount()

	def cal_total_amount(self):
		child_len = len(self.provisions)
		for pro in self.provisions:
			if pro.idx == child_len:
				total_amount = pro.provision
		self.total_amount = total_amount