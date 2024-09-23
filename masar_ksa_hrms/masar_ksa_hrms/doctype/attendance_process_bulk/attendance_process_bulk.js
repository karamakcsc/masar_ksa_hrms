// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Process Bulk", {
	refresh(frm) {
        get_date_period(frm);
        if(frm.doc.__islocal != 1 && frm.doc.docstatus === 0){
            frm.add_custom_button(__('Get Employees'), function(){
                frappe.call({
                    doc:frm.doc,
                    method:"get_employees",
                    callback:function(r){
                        refresh_field("employees");
                        frm.refresh_field("employees_no");
                    }
                })
            });
            
        }
        if(frm.doc.docstatus===1){
            frm.add_custom_button(__('Submit Attendance Process'),function(){
                frappe.call({
                    doc:frm.doc,
                    method:'submit_all_attendance_processes',
                    callback:function(r){
                    }
                })
            })
        }
        
	},
    after_cancel:function(frm){
        frm.refresh();
    }

});

function get_date_period(frm){
    frappe.call({
        doc:frm.doc,
        method:'get_date_period',
        callback: function(r){
            refresh_field("from_date");
            refresh_field("to_date");
        }
    });
}