import frappe
from frappe import _
from frappe.model.document import Document
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation
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
            eos_validation(self ,table_name = 'res_periods_table' , rate_name = 'rate')