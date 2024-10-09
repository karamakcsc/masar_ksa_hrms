frappe.ui.form.on("Employee Incentive Bulk", {
    refresh: function(frm) {
        // FilterFields(frm); 
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
    }
});
