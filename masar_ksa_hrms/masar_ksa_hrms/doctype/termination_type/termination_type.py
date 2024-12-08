import frappe
from frappe import _
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation
from frappe.utils import get_link_to_form
class TerminationType(Document):
    def validate(self):
        self.validation_checks()

    def validation_checks(self):
        if self.is_resignation:
            tt = frappe.qb.DocType('Termination Type')
            resignation_type = (
                frappe.qb.from_(tt)
                .where(tt.is_resignation == 1 )
                .where(tt.name != self.name)
                .select(tt.name)
            ).run(as_dict = True)
            if len(resignation_type) == 1:
                exist_resignation = resignation_type[0]['name']
                frappe.throw("Only one Resignation Type is allowed.<br>A Resignation has Already Been Defined in <b>{exist_resignation}</b>."
                             .format(exist_resignation = get_link_to_form(self.doctype , exist_resignation)),
                             title=_("Validation Error"))
            eos_validation(self ,table_name = 'res_periods_table' , rate_name = 'rate')