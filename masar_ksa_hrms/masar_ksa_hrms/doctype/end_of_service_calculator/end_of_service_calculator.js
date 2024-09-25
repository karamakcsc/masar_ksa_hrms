// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("End of Service Calculator", {
    calculate: function(frm) {
        frappe.call({
            doc: frm.doc,
            method:'calculate_eos'
        })
	},
});
