// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Shortage", {
	posting_date: function(frm) {
        GetDatePeriod(frm);
	},
    onload: function(frm) {
        GetDatePeriod(frm);
        FilterInChildTable(frm);
	},
    refresh: function(frm, cdt, cdn){
        GetDatePeriod(frm);
        FilterInChildTable(frm);
        frm.add_custom_button(__('Get Attendance'), function(){
            frappe.call({
                doc:frm.doc,
                method:"get_shortage_attendance",
                callback:function(r){
                    refresh_field("attendance");
                    child_shift_assignment(frm);
                }
            })
        });
        set_query(frm, cdt, cdn);
        set_query_if_bulk(frm);
        shift_assignment(frm);
        child_shift_assignment(frm);
    },
    action_type:function(frm){
        set_query_if_bulk(frm);
    },
    is_bulk:function(frm){
        set_query_if_bulk(frm);
    },
    employee:function(frm){
        shift_assignment(frm);
    },
    shift_assignment:function(frm){
        child_shift_assignment(frm);
    },
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
function FilterInChildTable(frm) {
    frm.set_query("short_leave_application", "attendance", function (doc, cdt, cdn) {
        var sla = [];
        if (doc.attendance && doc.attendance.length) {
            sla = doc.attendance.map(item => item.short_leave_application);
        }
        return {
            filters: [
                ['Short Leave Application', 'employee', '=', frm.doc.employee],
                ['Short Leave Application', 'name', 'not in', sla]
            ]
        };
    });
    frm.set_query("shift_assignment", "attendance", function (doc, cdt, cdn) {
        return {
            filters: [
                ['Shift Assignment', 'employee', '=', frm.doc.employee],
                ['Shift Assignment' , 'docstatus' , '=' , 1 ]
            ]
        };
    });
    frm.set_query("salary_component", "attendance", function (doc, cdt, cdn) {
        return {
            filters: [
                ['Salary Component', 'custom_salary_deduction', '=',1],
            ]
        };
    });
}

frappe.ui.form.on("Attendance Shortage Details", {
    
    action_type: function(frm, cdt, cdn) {
        frm.refresh();
        set_query(frm, cdt, cdn);
    },
    onload:function(frm,cdt,cdn){
        frm.refresh()
        set_query(frm,cdt,cdn);
    },
    refresh:function(frm,cdt,cdn){
        frm.refresh();
        set_query(frm,cdt,cdn);
    },
});
function set_query(frm, cdt, cdn) {
    var child_table = frm.fields_dict['attendance'];
    var leave_field = child_table.grid.get_field('leave_type');

    if (leave_field) {
        leave_field.get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            if (child.action_type === 'Salary Deduction') {
                return {
                    filters: [
                        ['Leave Type', 'custom_salary_deduction', '=', 1]
                    ]
                };
            } else if (child.action_type === 'Balance Deduction') {
                return {
                    filters: [
                        ['Leave Type', 'custom_balance_deduction', '=', 1]
                    ]
                };
            } 
        };
    } 
    frm.refresh_field('attendance');
}
function set_query_if_bulk(frm){
    
    if(frm.doc.is_bulk){
        if(frm.doc.action_type==='Salary Deduction'){
            
            frm.set_query("leave_type", function() {
                return{
                    filters:[
                        ['Leave Type' , 'custom_salary_deduction', '=' , 1]
                    ]
                }
            });
            frm.set_query("salary_component", function () {
                return {
                    filters: [
                        ['Salary Component', 'custom_salary_deduction', '=',1],
                    ]
                };
            });
        }
        else if (frm.doc.action_type==='Balance Deduction'){
            frm.set_query("leave_type", function() {
                return{
                    filters:[
                        ['Leave Type' , 'custom_balance_deduction', '=' , 1]
                    ]
                }
            })
        }
        else{
            frm.set_query("leave_type", function() {
                return{
                    filters:[
                        [ 'Leave Type' , 'custom_balance_deduction', '=' , 0],
                        ['Leave Type' , 'custom_salary_deduction', '=' , 0]
                    ]
                }
            })
        }

    }
    
}
function shift_assignment(frm){
    if(frm.doc.employee){
        frm.set_query('shift_assignment',function() {
            return{
                filters:{
                    employee : frm.doc.employee , 
                    docstatus : 1 
                }
            }
        })
    }
}
function child_shift_assignment(frm){
    if(frm.doc.shift_assignment){
        $.each(frm.doc.attendance,  function(i,  d){
            d.shift_assignment=frm.doc.shift_assignment;
        } )
    }
    else{
        $.each(frm.doc.attendance,function(i,d){
            d.shift_assignment="";
        })
    }
}
