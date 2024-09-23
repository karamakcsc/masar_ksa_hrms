frappe.ui.form.on("Salary Component", {
    refresh: function(frm) {
        formula_display(frm);
    },
    setup: function(frm) {
        formula_display(frm);
    },
    onload: function(frm) {
        formula_display(frm);
    },
    custom_formula_check: function(frm) {
        formula_display(frm);
    }
});

function formula_display(frm) {
    if (frm.doc.custom_formula_check === 1) {
        frm.toggle_display("formula", false);
        hrms.payroll_utils = {
            set_autocompletions_for_condition_and_formula: function(frm, child_row = "") {
                const autocompletions = [];

                frappe.run_serially([
                    ...["Employee", "Employee Salary Component Detail", "Salary Structure", "Salary Structure Assignment", "Salary Slip"].map(
                        (doctype) =>
                            frappe.model.with_doctype(doctype, () => {
                                autocompletions.push(
                                    ...frappe.get_meta(doctype).fields.map((f) => ({
                                        value: f.fieldname,
                                        score: 8,
                                        meta: __("{0} Field", [doctype]),
                                    })),
                                );
                            }),
                    ),
                    () => {
                        frappe.db.get_list("Salary Component", {
                            fields: ["salary_component_abbr"],
                        }).then((salary_components) => {
                            autocompletions.push(
                                ...salary_components.map((d) => ({
                                    value: d.salary_component_abbr,
                                    score: 9,
                                    meta: __("Salary Component"),
                                })),
                            );

                            autocompletions.push(
                                ...["base", "variable"].map((d) => ({
                                    value: d,
                                    score: 10,
                                    meta: __("Salary Structure Assignment field"),
                                })),
                            );

                            if (child_row) {
                                ["condition", "formula"].forEach((field) => {
                                    frm.set_df_property(
                                        child_row.parentfield,
                                        "autocompletions",
                                        autocompletions,
                                        frm.doc.name,
                                        field,
                                        child_row.name,
                                    );
                                });

                                frm.refresh_field(child_row.parentfield);
                            } else {
                                ["condition", "formula"].forEach((field) => {
                                    frm.set_df_property(field, "autocompletions", autocompletions);
                                });
                            }
                        });
                    },
                ]);
            },
        };
        hrms.payroll_utils.set_autocompletions_for_condition_and_formula(frm);
        if (!frm.doc.__islocal) {
            frm.trigger("add_update_structure_button");
            frm.add_custom_button(
                __("Salary Structure"),
                () => {
                    frm.trigger("create_salary_structure");
                },
                __("Create"),
            );
        }

        // Call the custom formula to update the formula (Zaid)
        frappe.call({
            method: "masar_ksa_hrms.custom.salary_component.salary_component.update_formula_via_api",
            args: {
                docname: frm.doc.name,
                formula_value: "esc_amount"
            },
        });
    } else {
        frm.toggle_display("formula", true);
    }
}

frappe.ui.form.on("Salary Component", {
    add_update_structure_button: function(frm) {
        ["Condition", "Formula"].forEach((df) => {
            frm.add_custom_button(
                __("Sync {0}", [df]),
                function() {
                    frappe.call({
                        method: "get_structures_to_be_updated",
                        doc: frm.doc,
                    }).then((r) => {
                        if (r.message.length) {
                            frm.events.update_salary_structures(frm, df, r.message);
                        } else {
                            frappe.msgprint({
                                message: __(
                                    "Salary Component {0} is currently not used in any Salary Structure.",
                                    [frm.doc.name.bold()],
                                ),
                                title: __("No Salary Structures"),
                                indicator: "orange",
                            });
                        }
                    });
                },
                __("Update Salary Structures"),
            );
        });
    },
    create_salary_structure: function(frm) {
        frappe.model.with_doctype("Salary Structure", () => {
            const salary_structure = frappe.model.get_new_doc("Salary Structure");
            const salary_detail = frappe.model.add_child(
                salary_structure,
                frm.doc.type === "Earning" ? "earnings" : "deductions",
            );
            salary_detail.salary_component = frm.doc.name;
            frappe.set_route("Form", "Salary Structure", salary_structure.name);
        });
    }
});
