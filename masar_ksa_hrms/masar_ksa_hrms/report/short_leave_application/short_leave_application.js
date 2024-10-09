// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Short Leave Application"] = {
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
			fieldname: "leave_approver",
			label: __("Leave Approver"),
			fieldtype: "Link",
			options: "User",
		},
		{
			fieldname: "shift_assignment",
			label: __("Shift Assignment"),
			fieldtype: "Link",
			options: "Shift Assignment",
		}

	]
};
