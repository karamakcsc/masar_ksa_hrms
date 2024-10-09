// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Attendance Process"] = {
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
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
	]
};
