# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OvertimeType(Document):
    def validate(self):
        self.check_overtime_type()

    def check_overtime_type(self):
        _type = float(self.normal_day) + float(self.off_day) + float(self.holidays)
        if _type != 1:
            frappe.throw(_('Please choose only one or at least one Overtime Type'), title=_('Overtime Type'))

        if self.rate in [None, "", 0]:
            frappe.throw(_('Hour Rate cannot be zero'), title=_('Hour Rate'))
            
        if self.normal_day == 1 or self.off_day == 1 or self.holidays == 1:
            conditions = []
            if self.normal_day == 1:
                conditions = "normal_day = 1"
            if self.off_day == 1:
                conditions = "off_day = 1"
            if self.holidays == 1:
                conditions = "holidays = 1"
            exist_type = None
            query = f"SELECT name FROM `tabOvertime Type` WHERE {conditions}"
            existing_types = frappe.db.sql(query, as_dict=True)
            if existing_types and existing_types[0] and existing_types[0]["name"]:
                  exist_type = existing_types[0]["name"]
            if  exist_type is not None and self.normal_day == 1:
                  frappe.throw(f"Normal Day Type already exists in <b>{exist_type}</b>", title=_("Exist Normal Day Type"))
            if self.off_day == 1 and exist_type is not None:
                  frappe.throw(f"Off Day Type already exists in <b>{exist_type}</b>", title=_("Exist Off Day Type"))
            if self.holidays == 1 and exist_type is not None:
                  frappe.throw(f"Holidays Type already exists in <b>{exist_type}</b>", title=_("Exist Holidays Type"))

