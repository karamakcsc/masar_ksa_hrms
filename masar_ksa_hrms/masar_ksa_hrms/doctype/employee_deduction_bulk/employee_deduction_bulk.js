// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Deduction Bulk", {
	refresh: function(frm) {
        FilterFields(frm);
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
    setup: function(frm) {
        FilterFields(frm);
    },
    onload: function(frm) { 
        FilterFields(frm);
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


function FilterFields(frm) { 
    frm.set_query('salary_component', function() {
        return {
            filters: {
                "type": "Deduction",
            }
        };
    });
}