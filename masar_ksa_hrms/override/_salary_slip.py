# import math
# from datetime import date

# import frappe
# from frappe import _, msgprint
# from frappe.model.naming import make_autoname
# from frappe.query_builder import Order
# from frappe.query_builder.functions import Sum
# from frappe.utils import (
# 	add_days,
# 	cint,
# 	cstr,
# 	date_diff,
# 	flt,
# 	formatdate,
# 	get_first_day,
# 	get_link_to_form,
# 	getdate,
# 	money_in_words,
# 	rounded,
# )
# from frappe.utils.background_jobs import enqueue

# import erpnext
# from erpnext.accounts.utils import get_fiscal_year
# # from erpnext.loan_management.doctype.loan_repayment.loan_repayment import (
# # 	calculate_amounts,
# # 	create_repayment_entry,
# # )
# # from erpnext.loan_management.doctype.process_loan_interest_accrual.process_loan_interest_accrual import (
# # 	process_loan_interest_accrual_for_term_loans,
# # )
# # from erpnext.utilities.transaction_base import TransactionBase

# # from hrms.hr.utils import get_holiday_dates_for_employee, validate_active_employee
# # from hrms.payroll.doctype.additional_salary.additional_salary import get_additional_salaries
# # from hrms.payroll.doctype.employee_benefit_application.employee_benefit_application import (
# # 	get_benefit_component_amount,
# # )
# # from hrms.payroll.doctype.employee_benefit_claim.employee_benefit_claim import (
# # 	get_benefit_claim_amount,
# # 	get_last_payroll_period_benefits,
# # )
# # from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
# # from hrms.payroll.doctype.payroll_period.payroll_period import (
# # 	get_payroll_period,
# # 	get_period_factor,
# # )
# # from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
# # from hrms.hr.payroll.doctype.salary_slip.salary_slip import calculate_lwp_ppl_and_absent_days_based_on_attendance


# def get_working_days_details(self, lwp=None, for_preview=0):
#     payroll_settings = frappe.get_cached_value(
#         "Payroll Settings",
#         None,
#         (
#             "payroll_based_on",
#             "include_holidays_in_total_working_days",
#             "consider_marked_attendance_on_holidays",
#             "daily_wages_fraction_for_half_day",
#             "consider_unmarked_attendance_as",
#         ),
#         as_dict=1,
#     )

#     consider_marked_attendance_on_holidays = (
#         payroll_settings.include_holidays_in_total_working_days
#         and payroll_settings.consider_marked_attendance_on_holidays
#     )

#     daily_wages_fraction_for_half_day = (
#         flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5
#     )

#     working_days = 30
#     if for_preview:
#         self.total_working_days = working_days
#         self.payment_days = working_days
#         return

#     holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
#     working_days_list = [
#         add_days(getdate(self.start_date), days=day) for day in range(0, working_days)
#     ]

#     if not cint(payroll_settings.include_holidays_in_total_working_days):
#         working_days_list = [i for i in working_days_list if i not in holidays]

#         working_days -= len(holidays)
#         if working_days < 0:
#             frappe.throw(_("There are more holidays than working days this month."))

#     if not payroll_settings.payroll_based_on:
#         frappe.throw(_("Please set Payroll based on in Payroll settings"))

#     if payroll_settings.payroll_based_on == "Attendance":
#         actual_lwp, absent = self.calculate_lwp_ppl_and_absent_days_based_on_attendance(
#             holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
#         )
#         self.absent_days = absent
#     else:
#         actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(
#             holidays, working_days_list, daily_wages_fraction_for_half_day
#         )

#     if not lwp:
#         lwp = actual_lwp
#     elif lwp != actual_lwp:
#         frappe.msgprint(
#             _("Leave Without Pay does not match with approved {} records").format(
#                 payroll_settings.payroll_based_on
#             )
#         )

#     self.leave_without_pay = lwp
#     self.total_working_days = working_days

#     payment_days = 30

#     if flt(payment_days) > flt(lwp):
#         self.payment_days = flt(payment_days) - flt(lwp)

#         if payroll_settings.payroll_based_on == "Attendance":
#             self.payment_days -= flt(absent)

#         consider_unmarked_attendance_as = payroll_settings.consider_unmarked_attendance_as or "Present"

#         if (
#             payroll_settings.payroll_based_on == "Attendance"
#             and consider_unmarked_attendance_as == "Absent"
#         ):
#             unmarked_days = self.get_unmarked_days(payroll_settings.include_holidays_in_total_working_days)
#             self.absent_days += unmarked_days  # will be treated as absent
#             self.payment_days -= unmarked_days
#     else:
#         self.payment_days = 0

# def calculate_lwp_ppl_and_absent_days_based_on_attendance(
#     self, holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
# ):
#     lwp = 0
#     absent = 0

#     leave_type_map = self.get_leave_type_map()
#     attendance_details = self.get_employee_attendance(
#         start_date=self.start_date, end_date=self.actual_end_date
#     )

#     for d in attendance_details:
#         if (
#             d.status in ("Half Day", "On Leave")
#             and d.leave_type
#             and d.leave_type not in leave_type_map.keys()
#         ):
#             continue

#         # skip counting absent on holidays
#         if not consider_marked_attendance_on_holidays and getdate(d.attendance_date) in holidays:
#             if d.status == "Absent" or (
#                 d.leave_type
#                 and d.leave_type in leave_type_map.keys()
#                 and not leave_type_map[d.leave_type]["include_holiday"]
#             ):
#                 continue

#         if d.leave_type:
#             fraction_of_daily_salary_per_leave = leave_type_map[d.leave_type][
#                 "fraction_of_daily_salary_per_leave"
#             ]

#         if d.status == "Half Day":
#             equivalent_lwp = 1 - daily_wages_fraction_for_half_day

#             if d.leave_type in leave_type_map.keys() and leave_type_map[d.leave_type]["is_ppl"]:
#                 equivalent_lwp *= (
#                     fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
#                 )
#             lwp += equivalent_lwp

#         elif d.status == "On Leave" and d.leave_type and d.leave_type in leave_type_map.keys():
#             equivalent_lwp = 1
#             if leave_type_map[d.leave_type]["is_ppl"]:
#                 equivalent_lwp *= (
#                     fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
#                 )
#             lwp += equivalent_lwp

#         elif d.status == "Absent":
#             absent += 1

#     return lwp, absent

# def get_leave_type_map(self) -> dict:
# 		"""Returns (partially paid leaves/leave without pay) leave types by name"""

# 		def _get_leave_type_map():
# 			leave_types = frappe.get_all(
# 				"Leave Type",
# 				or_filters={"is_ppl": 1, "is_lwp": 1},
# 				fields=["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"],
# 			)
# 			return {leave_type.name: leave_type for leave_type in leave_types}

# 		return frappe.cache().get_value(LEAVE_TYPE_MAP, _get_leave_type_map)
