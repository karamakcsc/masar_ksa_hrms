// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Shift Management Bulk", {
	refresh(frm) {
        if(frm.doc.__islocal != 1  && frm.doc.docstatus === 0){
        frm.add_custom_button(__('Get Employees'), function(){
            frappe.call({
                doc:frm.doc,
                method:"get_employees",
                callback:function(r){
                    refresh_field("emp_table");
                }
            })
        });
    }
	},
});
