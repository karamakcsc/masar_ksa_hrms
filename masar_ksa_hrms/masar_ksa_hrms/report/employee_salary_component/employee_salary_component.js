// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Salary Component"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "from",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "salary_component",
			label: __("Salary Component"),
			fieldtype: "Link",
			options: "Salary Component",
		},
		{
			fieldname: "is_active",
			label: __("Is Active"),
			fieldtype: "Check",
			// default: 1,
		}

	]
};
