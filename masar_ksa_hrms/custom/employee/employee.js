frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.set_query("salary_component", "custom_employee_salary_component", function(doc, cdt, cdn) {

            return {
                filters: {
                    custom_formula_check : 1
                }
            };
        });
    }
});