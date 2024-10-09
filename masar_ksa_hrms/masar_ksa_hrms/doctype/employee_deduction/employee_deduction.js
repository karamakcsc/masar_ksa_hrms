// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Deduction", {
	refresh(frm) {
        filter_field(frm);
	},
    onload(frm) {
        filter_field(frm);
    },
    setup(frm) {
        filter_field(frm);
    }
});


function filter_field(frm) {
    frm.fields_dict['salary_component'].get_query = function(frm) {
        return {
            filters: {
                "type": "Deduction",
            }
        };
    };
}
