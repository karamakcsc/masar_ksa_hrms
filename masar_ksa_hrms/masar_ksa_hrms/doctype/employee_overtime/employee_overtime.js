// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee Overtime", {
// 	refresh(frm) {

// 	},
// });
cur_frm.fields_dict['employee'].get_query = function(doc) {
	return {
		filters: {
			"is_overtime_applicable": 1
		}
	}
}

cur_frm.fields_dict['salary_component'].get_query = function(doc) {
	return {
		filters: {
			"is_overtime_applicable": 1
		}
	}
}

cur_frm.fields_dict['salary_structure_assignment'].get_query = function(doc) {
	return {
		filters: {
			"docstatus": 1,
			"employee": doc.employee
		}
	}
}



frappe.ui.form.on("Employee Overtime", {
    refresh: function(frm) {
        rate_wd(frm);
        rate_off_day(frm);
    },
    overtime_hours_working_day: function(frm) {
        rate_wd(frm);
        amount_wd(frm);
        calculate_total(frm);
    },
    overtime_hours_off_day: function(frm) {
        rate_off_day(frm);
        amount_off_day(frm);
        calculate_total(frm);
    },
    validate: function(frm) {
        rate_off_day(frm);
        amount_off_day(frm);
        calculate_total(frm);
    },
    setup: function(frm) {
        rate_off_day(frm);
        amount_off_day(frm);
        calculate_total(frm);
    },
    on_submit: function(frm) {
        rate_off_day(frm);
        amount_off_day(frm);
        calculate_total(frm);
    },
});

var rate_wd = function(frm) {
    var doc = frm.doc;
    frm.set_value("rate_hours_working_day", doc.basic_salary / 240 * doc.overtime_rate_working_hour);
};

var rate_off_day = function(frm) {
    var doc = frm.doc;
    frm.set_value("rate_hours_off_day", doc.basic_salary / 240 * doc.overtime_rate_off_day);
};

var amount_wd = function(frm) {
    var doc = frm.doc;
    frm.set_value("amount_working_day", doc.rate_hours_working_day * doc.overtime_hours_working_day);
};

var amount_off_day = function(frm) {
    var doc = frm.doc;
    frm.set_value("amount_off_day", doc.rate_hours_off_day * doc.overtime_hours_off_day);
};

var calculate_total = function(frm) {
    var doc = frm.doc;
    frm.set_value("total_amount", flt(doc.amount_working_day) + flt(doc.amount_off_day));
};
