// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Type", {
	refresh: function(frm) {
        GetFilter(frm);
	},
    onload:function(frm) {
        GetFilter(frm);
	},
    setup:function(frm) {
        GetFilter(frm);
	},
});
function GetFilter(frm){
    frm.set_query("salary_component", function () {
        return {
            filters: {
                type: 'Earning',
            },
        };
    });
}
