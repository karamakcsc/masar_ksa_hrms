import frappe
from frappe import _ 

def validate(self , method ):
    check_grace_period(self)

def check_grace_period(self):
    if self.custom_enable_early_entry_marking and self.custom_early_entry_grace_period <= 0 :
        frappe.throw("Eraly Enrty Grace Period Must be more than Zero." , title="Missing Early Entry Grace Period")
    if self.custom_enable_late_exit_marking and self.custom_late_exit_grace_period <= 0 :
        frappe.throw("Late Exit Grace Period Must be more than Zero." , title="Missing Late Exit Grace Period")
