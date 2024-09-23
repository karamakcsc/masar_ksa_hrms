import frappe
from frappe import _
from frappe.model.document import Document

class TerminationType(Document):
    def validate(self):
        self.validation_checks()

    def validation_checks(self):
        if self.is_resignation:
            resignation_type = frappe.db.sql("""
                SELECT name FROM `tabTermination Type`
                WHERE is_resignation = 1 AND name != %s
            """, (self.name,), as_dict=True)
            
            if len(resignation_type) == 1:
                exist_resignation = resignation_type[0]['name']
                frappe.throw(f"Only one Resignation Type is allowed.<br>A resignation has already been defined in <b>{exist_resignation}</b>.",
                             title=_("Validation Error"))

        next_year = None
        last_row = len(self.res_periods_table)

        for  reg in self.res_periods_table:

            if reg.rate > 100:
                frappe.throw(_("Rate cannot be greater than 100. In Row {idx}".format(idx=reg.idx)),
                             title=_("Rate Error"))
            if reg.idx < last_row and reg.from_year >= reg.to_year:
                frappe.throw(_("The 'From Year' in Row {idx} must be less than 'To Year'.".format(idx=reg.idx)),
                             title=_("Year Range Error"))
            if next_year is not None:
                if reg.from_year < next_year:
                    frappe.throw(_("The 'From Year' in Row {idx} cannot be less than the 'To Year' of the previous row (Row {previous_idx}).".format(idx=reg.idx, previous_idx=reg.idx - 1)),
                                 title=_("Year Range Error"))
                elif reg.from_year > next_year:
                    frappe.throw(_("The 'From Year' in Row {idx} must be equal to the 'To Year' of the previous row (Row {previous_idx}). It should be {next_year}.".format(idx=reg.idx, previous_idx=reg.idx - 1, next_year=next_year)),
                                 title=_("Year Range Error"))
            if reg.idx == last_row:
                if reg.has_period != 0:
                    frappe.throw(_("The 'has_period' in the last row must be set to 0."), title=_("Period Error"))
                if reg.to_year:
                    frappe.throw(_("The last row should not have a 'to_year' value."), title=_("Year Error"))
            else:
                if reg.has_period != 1:
                    frappe.throw(_("All rows except the last one must have 'has_period' set to 1. In Row {idx}".format(idx=reg.idx)),
                                 title=_("Period Error"))
                if not reg.to_year:
                    frappe.throw(_("All rows with 'has_period' set to 1 must have a 'to_year' value. In Row {idx}".format(idx=reg.idx)),
                                 title=_("Year Error"))
            next_year = reg.to_year
