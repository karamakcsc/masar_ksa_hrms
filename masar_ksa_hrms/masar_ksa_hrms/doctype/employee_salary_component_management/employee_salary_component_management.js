// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Salary Component Management", {
    refresh: function(frm) {
        Filters(frm);
    },
    setup: function(frm) {
        Filters(frm);
    },
    onload: function(frm) {
        Filters(frm);
    },
    employee: function(frm) {
        GetSSNumber(frm)
    },
    company: function(frm) {
        GetBasicSalaryComponent(frm);
    },
    by_percent : function(frm) { 
        GetHousingPercentage(frm)
    }, 
    percentage: function(frm) { 
        GetHousingAmount(frm);
    },
    default_percent : function(frm) { 
        GetHousingPercentage(frm)
    },
    calculate:function(frm) {
        Calculations(frm);
    }, 
    ss_salary:function(frm){
        SSAmount(frm);
    }

});
function Calculations(frm) {
    frappe.call({
        doc:frm.doc, 
        method :'salary_calculation',
        callback: function(r){
            frm.set_value('deduction_salary', r.message.deduction_salary);
            frm.refresh_field('deduction_salary');
            frm.set_value('basic_salary_with_allowance', r.message.basic_salary_with_allowance);
            frm.refresh_field('basic_salary_with_allowance');
            frm.set_value('ss_salary', r.message.ss_salary);
            frm.refresh_field('ss_salary');
            frm.set_value('eos_salary', r.message.eos_salary);
            frm.refresh_field('eos_salary');
            SSAmount(frm);
        }
    })
}
function Filters(frm) {
    frm.set_query('housing_component', function() {
        return {
            filters: {
                "type": "Earning",
                'custom_is_housing_allowance': 1
            }
        };
    });
    frm.set_query('ss_component', function() {
        return {
            filters: {
                "type": "Deduction",
            }
        };
    });
    frm.set_query('end_of_service_rate', function() {
        return {
            filters: {
                "docstatus": 1,
                "employee": frm.doc.employee,
            }
        };
    });
    frappe.db.get_value('Company', frm.doc.company, 'custom_salary_component').then((r) => {
        frm.fields_dict["esc_table"].grid.get_field("salary_component").get_query = function () {
            let salComp = [];
    
            if (frm.doc.esc_table && frm.doc.esc_table.length) {
                salComp = frm.doc.esc_table.map(row => row.salary_component);
            }
    
            return {
                filters: [
                    ["name", "not in", [r.message.custom_salary_component , frm.doc.ss_component]], 
                    ["custom_is_housing_allowance", "=", 0],
                    ["name", "not in", salComp] 
                ]
            };
        };
    });
    

}
function GetBasicSalaryComponent(frm){
    frappe.call({
        doc: frm.doc,
        method: 'get_basic_salary_component',
        callback: function(r) {
            let basicSalary = r.message;
            frm.set_value('basic_salary_component', basicSalary);
            frm.refresh_field('basic_salary_component');
            frm.set_query('basic_salary_component', function() {
                return {
                    filters: {
                        "type": "Earning",
                        "name": basicSalary
                    }
                };
            });
            Filters(frm);
        }
    });
}
function GetSSNumber(frm){
    frappe.call({
        doc: frm.doc,
        method: 'get_emp_social_security_info',
        callback: function(r) {
            frm.set_value('ss_number', r.message.number);
            frm.refresh_field('ss_number');
            frm.set_value('ss_start_date', r.message.date);
            frm.refresh_field('ss_start_date');
            Filters(frm);
        }
    });
}

function GetHousingAmount(frm) {
    frappe.call({
        doc:frm.doc , 
        method : 'get_housing_amount',
        callback: function(r) { 
            frm.set_value('housing_amount', r.message);
            frm.refresh_field('housing_amount');
        }
    });
}
function GetHousingPercentage(frm){
    frappe.call({
        doc : frm.doc , 
        method : 'get_housing_percentage',
        callback: function(r){
            frm.set_value('percentage', r.message);
            frm.refresh_field('percentage');
            frappe.call({
                doc:frm.doc , 
                method : 'get_housing_amount',
                callback: function(r) { 
                    frm.set_value('housing_amount', r.message);
                    frm.refresh_field('housing_amount');
                }
            })
        }
    });
}
function SSAmount(frm){
    frappe.call({
        doc:frm.doc,
        method: 'calculate_ss_amount',
        callback: function(r) { 
            frm.set_value('ss_amount', r.message);
            frm.refresh_field('ss_amount');
        }
    })
}