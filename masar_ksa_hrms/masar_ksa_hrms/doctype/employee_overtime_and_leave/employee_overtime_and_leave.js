// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Overtime and Leave", {
	posting_date: function(frm) {
        GetDatePeriod(frm);
	},
    onload: function(frm) {
        GetDatePeriod(frm);
	},
    refresh: function(frm){

        GetDatePeriod(frm);
    },
    overtime_nd: function(frm){
        OvertimeAmount(frm)
    },
    overtime_od: function(frm){
        OvertimeAmount(frm)
    },
    overtime_hd: function(frm){
        OvertimeAmount(frm)
    }, 
    overtime_type_nd: function(frm){
        ResetZeroOvertime(frm)
    },
    overtime_type_od: function(frm){
        ResetZeroOvertime(frm)
    },
    overtime_type_hd: function(frm){
        ResetZeroOvertime(frm)
    }
});
function GetDatePeriod(frm){
    frappe.call({
        doc:frm.doc,
        method:'get_date_period',
        callback: function(r){
            refresh_field("from_date");
            refresh_field("to_date");
        }
    });
}
function  OvertimeAmount(frm){
    frappe.call({
        doc:frm.doc,
        method:'overtime_amount_calculations',
        callback: function(r){
            refresh_field("amount_nd");
            refresh_field("amount_od");
            refresh_field("amount_hd");
            refresh_field("total_nd");
            refresh_field("total_od");
            refresh_field("total_hd");
            refresh_field("ot_total_amount");

        }
    })
}
function ResetZeroOvertime(frm){
    if (!frm.doc.overtime_type_nd){
        frm.doc.overtime_nd = 0 ;
        frm.doc.amount_nd= null;
        refresh_field("overtime_nd");
        refresh_field("amount_nd");
    }
    if (!frm.doc.overtime_type_od){
        frm.doc.overtime_od = 0 ;
        frm.doc.amount_od= null;
        refresh_field("overtime_od");
        refresh_field("amount_od");
    }
    if (!frm.doc.overtime_type_hd){
        frm.doc.overtime_hd = 0 ;
        frm.doc.amount_hd= null;
        refresh_field("overtime_hd");
        refresh_field("amount_hd");
    }
}
