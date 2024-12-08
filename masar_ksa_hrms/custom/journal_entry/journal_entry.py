import frappe
from frappe import _

def before_cancel(self , method):
    for account in self.accounts:
        if (
            account.reference_type == 'Payroll Entry'  and account.user_remark is not None 
            and 'End of Service' in account.user_remark
            ):
                pro = 'EOS Provision Details'
                eosp = 'End of Service Provision'
                eospd = frappe.qb.DocType(pro)
                rows = (
                    frappe.qb.from_(eospd)
                    .select((eospd.name),
                            (eospd.parent)
                    )
                    .where(eospd.ref_jv == self.name)
                    ).run(as_dict = True)
                if len(rows) != 0:
                    for row in rows:
                        try:
                            frappe.delete_doc(pro , row.name)
                            eosp_doc = frappe.get_doc(eosp,row.parent)
                            child_len = len(eosp_doc.provisions)
                            for provision in eosp_doc.provisions:
                                if provision.idx == child_len:
                                    total_amount = provision.provision
                            eosp_doc.total_amount = total_amount
                            eosp_doc.run_method('save')
                        except Exception as ex : 
                            frappe.throw (f"Error Deleting Document {row.name} From {row.parent}: {str(ex)}")
                break
