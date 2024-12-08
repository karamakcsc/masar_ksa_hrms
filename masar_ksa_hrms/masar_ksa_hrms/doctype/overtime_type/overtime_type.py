# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OvertimeType(Document):
    def validate(self):
        self.check_overtime_type()
        self.check_general()
    def check_overtime_type(self):
        _type = float(self.normal_day) + float(self.off_day) + float(self.holidays)
        if _type != 1:
            frappe.throw(_('Please choose only one Overtime Type'), title=_('Overtime Type'))

        if self.rate in [None, "", 0]:
            frappe.throw(_('Hour Rate cannot be zero'), title=_('Hour Rate'))
    def check_general(self):
        if self.is_general: 
            self.department=  None
