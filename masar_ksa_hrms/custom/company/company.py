import frappe
from frappe import _

def validate(self, method):
        validation_checks(self)

def validation_checks(self):

    next_year = None
    last_row = len(self.custom_comp_eos_table)

    for  reg in self.custom_comp_eos_table:

        if reg.salary_rate > 100:
            frappe.throw(_("Rate cannot exceed 100. In Row {idx}".format(idx=reg.idx)),
                            title=_("Rate Error"))
        if reg.idx < last_row and reg.from_year >= reg.to_year:
            frappe.throw(_("The 'From Year' in Row {idx} must be less than 'To Year'.".format(idx=reg.idx)),
                            title=_("Year Range Error"))
        if next_year is not None:
            if reg.from_year < next_year:
                frappe.throw(_("The From Year in Row {idx} cannot be less than the To Year of the previous row (Row {previous_idx}).".format(idx=reg.idx, previous_idx=reg.idx - 1)),
                                title=_("Year Range Error"))
            elif reg.from_year > next_year:
                frappe.throw(_("The From Year in Row {idx} must be equal to the To Year of the previous row (Row {previous_idx}). It should be {next_year}.".format(idx=reg.idx, previous_idx=reg.idx - 1, next_year=next_year)),
                                title=_("Year Range Error"))
        if reg.idx == last_row:
            if reg.has_period != 0:
                frappe.throw(_("The Has Period in the last row must be set to 0."), title=_("Period Error"))
            if reg.to_year:
                frappe.throw(_("The last row should not have a To Year value."), title=_("Year Error"))
        else:
            if reg.has_period != 1:
                frappe.throw(_("All Rows Except the Last one Must Have Has Period set to 1. In Row {idx}".format(idx=reg.idx)),
                                title=_("Period Error"))
            if not reg.to_year:
                frappe.throw(_("All Rows with  Has Period set to 1 must have a To Year value. In Row {idx}".format(idx=reg.idx)),
                                title=_("Year Error"))
        next_year = reg.to_year
