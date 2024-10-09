# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeSalaryComponentHistory(Document):
    def on_cancel(self):
        frappe.throw(
            '''This document cannot be canceled. Changes should be managed through the Employee Salary Component Management.''',
            title = frappe._("Validation Error")
        )

    def on_trash(self):
        frappe.throw(
            'This document cannot be deleted. Please manage changes through the Employee Salary Component Management.'
                     ,title = frappe._("Validation Error")
            )