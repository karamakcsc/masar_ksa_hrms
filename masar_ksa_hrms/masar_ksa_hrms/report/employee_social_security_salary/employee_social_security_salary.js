// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Social Security Salary"] = {
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
			fieldname: "is_active",
			label: __("Is Active"),
			fieldtype: "Check",
			default: 1,
		}
	]
};
