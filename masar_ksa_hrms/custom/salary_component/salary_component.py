import frappe
from frappe import _

@frappe.whitelist()
def update_formula_via_api(docname, formula_value):
    if not frappe.has_permission("Salary Component", "write", docname):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    frappe.db.set_value("Salary Component", docname, "formula", formula_value, update_modified=False)
    frappe.db.commit()
    
def validate(self , method):
    custom_validate(self)
    

def custom_validate(self):
    if self.type == 'Earning':
        if self.custom_salary_deduction:
            frappe.throw(   "Salary Component Cannot Earning and Salary Deduction" ,
                         title=_("Error Define") 
                        )
    elif self.type == 'Deduction':
        if self.custom_is_short_leave_applicable:
            frappe.throw(   "Salary Component Cannot Deduction and Short Leave Applicable" ,
                         title=_("Error Define") 
                        )
        if self.custom_is_overtime_applicable:
            frappe.throw(   "Salary Component Cannot Deduction and Overtime Applicable" ,
                         title=_("Error Define") 
                        )
        if self.custom_is_eos_applicable:
            frappe.throw(   "Salary Component Cannot Deduction and EOS Applicable" ,
                         title=_("Error Define") 
                        )
        if self.custom_is_ss_applicable:
            frappe.throw(   'Salary Component Cannot Deduction and Social Security Applicable' , 
                         title=_("Error Define")
                        )
