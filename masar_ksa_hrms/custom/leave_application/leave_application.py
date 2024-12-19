import frappe 


def on_submit(self , method):
    empty_short_leave_application_validation(self)
    
def empty_short_leave_application_validation(self): 
    if self.custom_sla_reference is not None : 
        frappe.throw(f'The Short Leave Application cannot contain any entries.' , title=frappe._('Validation Error'))