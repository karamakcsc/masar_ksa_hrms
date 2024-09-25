// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salaries Increment", {
    refresh:function(frm) {
        FilterFields(frm); 
    }, 
    setup:function(frm){
        FilterFields(frm);
    },
    onload: function(frm) { 
        FilterFields(frm);
    }
});


function FilterFields(frm) { 
    frm.set_query('salary_component', function() {
        return {
            filters: {
                "type": "Earning",
                "custom_formula_check": 1
            }
        };
    });

    frm.set_query('document_type', function() {
        return {
            filters: {
                "name": ["in", ['Country', 'Designation', 'Branch', 'Department', 'Employee Grade', 'Employment Type']]
            }
        };
    });  
}