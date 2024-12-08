frappe.ui.form.on("Employee Incentive Bulk", {
    refresh: function(frm) {
        if(frm.doc.__islocal != 1 && frm.doc.docstatus === 0) { 
            frm.add_custom_button(__('Get Employees'), function() {
                frappe.call({
                    doc: frm.doc,
                    method: "get_employees",
                    callback: function(r) {
                        refresh_field("employees");
                        frm.refresh_field("no_of_employee");
                    }
                });
            });
        }
    }, 
    by_amount: function(frm){
        if (frm.doc.by_amount === 0){
            frm.doc.percentage =0; 
            frm.refresh_field("percentage");
        }
    },
    by_percent: function(frm){
        if (frm.doc.by_percent === 0){
            frm.doc.amount =0; 
            frm.refresh_field("amount");
        }
    }
});
