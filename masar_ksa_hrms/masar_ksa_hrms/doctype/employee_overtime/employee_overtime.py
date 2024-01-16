# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
# from __future__ import unicode_literals
import erpnext, json
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate
import datetime
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.document import Document
from frappe.model.document import Document
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
from frappe.model.document import Document

class EmployeeOvertime(Document):
	def __init__(self, *args, **kwargs):
		super(EmployeeOvertime, self).__init__(*args, **kwargs)

	def on_submit(self):
		self.defAddAdditionalSalary()


	def defAddAdditionalSalary(self,submit=True):
		employee = self.employee
		salary_component = self.salary_component
		payroll_date = self.posting_date
		hour_rate_wd= flt(self.basic_salary) / 240 * self.overtime_rate_working_hour
		hour_rate_od= flt(self.basic_salary) / 240 * self.overtime_rate_off_day
		deduct_amount = flt(self.overtime_hours_working_day * hour_rate_wd)	+ flt(self.overtime_hours_off_day * hour_rate_od)
		entry = {
			"employee": self.employee,
			"salary_component": salary_component,
			"company": self.company,
			"currency": frappe.get_doc("Company", self.company).default_currency,
			"amount": flt(deduct_amount),
			"payroll_date": payroll_date,
		}
		(frappe.new_doc("Additional Salary")
			.update(entry)
			.insert(ignore_permissions=True, ignore_mandatory=True)).run_method('submit')
		frappe.db.commit()



# @frappe.whitelist()
# def get_employee_attendance(date_from, date_to):
# 	attendance_list = frappe.db.sql("""
# 		WITH AttSh AS (
# 			SELECT
# 				tas.employee,
# 				tas.employee_name,
# 				SUM(IFNULL(tas.difference_hours, 0)) AS shortage_hours
# 			FROM `tabAttendance Shortage` tas
# 			WHERE tas.is_overtime = 1 AND tas.attendance_date BETWEEN %s AND %s
# 			GROUP BY employee
# 		),
# 		LeaveSH AS (
# 			SELECT
# 				tsla.employee,
# 				tsla.employee_name,
# 				SUM(IFNULL(tsla.total_leave_hours, 0)) AS leave_hours
# 			FROM `tabShort Leave Application` tsla
# 			WHERE tsla.posting_date BETWEEN %s AND %s
# 			GROUP BY employee
# 		)
# 		SELECT
# 			a.employee,
# 			a.employee_name,
# 			IFNULL(shortage_hours, 0) AS shortage_hours,
# 			IFNULL(leave_hours, 0) AS leave_hours,
# 			IFNULL(shortage_hours, 0) - IFNULL(leave_hours, 0) AS not_covered_hours
# 		FROM AttSh a
# 		LEFT JOIN LeaveSh l ON a.employee = l.employee
# 	""", (date_from, date_to, date_from, date_to), as_dict=True)

# 	for attendance in attendance_list:
# 		result = get_salary_structure_assignment(attendance.employee)
# 		entry = {
# 			"employee": attendance.employee,
# 			# "date_from": date_from,
# 			# "date_to": date_to,
# 			"overtime_hours_working_day": attendance.shortage_hours,
# 			# "leave_hours": attendance.leave_hours,
# 			"not_covered_hours": attendance.not_covered_hours,
# 			"salary_structure_assignment": result
# 		}
# 		(frappe.new_doc("Employee Overtime")
# 			.update(entry)
# 			.insert(ignore_permissions=True, ignore_mandatory=True)
# 			.run_method('submit'))
# 		frappe.db.commit()


@frappe.whitelist()
def get_salary_structure_assignment(employee=None):
	result = frappe.get_list(
		"Salary Structure Assignment",
		filters={'employee': employee, 'docstatus': 1},
		fields=['name'],
		order_by='creation DESC',
		limit=1
	)

	if result:
		return result[0].name
	else:
		return 0


@frappe.whitelist()
def get_employee_attendance(date_from, date_to):
    attendance_list = frappe.db.sql("""
        WITH AttSh AS (
            SELECT
                tas.employee,
                tas.employee_name,
                SUM(IFNULL(tas.difference_hours, 0)) AS shortage_hours
            FROM `tabAttendance Shortage` tas
            WHERE tas.is_overtime = 1 AND tas.attendance_date BETWEEN %s AND %s
            GROUP BY employee
        ),
        ATTSH_OFD AS (
            SELECT
                tas.employee,
                tas.employee_name,
                SUM(IFNULL(tas.difference_hours, 0)) AS shortage_hours_wofd
            FROM `tabAttendance Shortage` tas
            WHERE tas.working_off_day = 1 AND tas.attendance_date BETWEEN %s AND %s
            GROUP BY employee
        ),
        LeaveSH AS (
            SELECT
                tsla.employee,
                tsla.employee_name,
                SUM(IFNULL(tsla.total_leave_hours, 0)) AS leave_hours
            FROM `tabShort Leave Application` tsla
            WHERE tsla.posting_date BETWEEN %s AND %s
            GROUP BY employee
        )
        SELECT
            a.employee,
            a.employee_name,
            IFNULL(a.shortage_hours, 0) AS shortage_hours,
            IFNULL(o.shortage_hours_wofd, 0) AS shortage_hours_wofd,
            IFNULL(l.leave_hours, 0) AS leave_hours,
            IFNULL(a.shortage_hours, 0) - IFNULL(l.leave_hours, 0) AS not_covered_hours
        FROM AttSh a
        LEFT JOIN LeaveSh l ON a.employee = l.employee
        LEFT JOIN ATTSH_OFD o ON a.employee = o.employee
    """, (date_from, date_to, date_from, date_to, date_from, date_to), as_dict=True)

    for attendance in attendance_list:
        result = get_salary_structure_assignment(attendance.employee)
        entry = {
            "employee": attendance.employee,
            # "date_from": date_from,
            # "date_to": date_to,
            "overtime_hours_working_day": attendance.shortage_hours,
            "overtime_hours_off_day": attendance.shortage_hours_wofd,
            # "leave_hours": attendance.leave_hours,
            "not_covered_hours": attendance.not_covered_hours,
            "salary_structure_assignment": result
        }
        (frappe.new_doc("Employee Overtime")
            .update(entry)
            .insert(ignore_permissions=True, ignore_mandatory=True)
            .run_method('submit'))
        frappe.db.commit()
