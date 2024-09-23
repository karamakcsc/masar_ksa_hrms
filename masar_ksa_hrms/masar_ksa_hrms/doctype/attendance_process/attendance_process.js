// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Process", {
	posting_date: function(frm) {
        GetDatePeriod(frm);
	},
    onload: function(frm) {
        DocFilters(frm);
        GetDatePeriod(frm);
	},
    refresh: function(frm){
        DocFilters(frm);
        GetDatePeriod(frm);
    },
    remove_linked_attendance:function(frm){
        frappe.call({
            doc :frm.doc,
            method:'remove_linked_attendance_overtime', 
            callback:function(r){
                refresh_field("connections_tab");
            }
        })
    },
    get_linked_attendance:function(frm){
        frappe.call({
            doc:frm.doc,
            method:'set_linked_attendance',
            callback:function(r){
                refresh_field("connections_tab");
            }
        }); 
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
function DocFilters(frm){
    frm.get_field('overtime_details').grid.cannot_add_rows = true;
    frm.set_query("sc_overtime_nd", function () {
        return {
            filters: {
                type: 'Earning',
                custom_is_overtime_applicable:1
            },
        };
    });
    frm.set_query("sc_overtime_od", function () {
        return {
            filters: {
                type: 'Earning',
                custom_is_overtime_applicable:1
            },
        };
    });
    frm.set_query("sc_overtime_hd", function () {
        return {
            filters: {
                type: 'Earning',
                custom_is_overtime_applicable:1
            },
        };
    });
}
