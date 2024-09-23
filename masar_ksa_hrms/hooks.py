app_name = "masar_ksa_hrms"
app_title = "Masar Ksa Hrms"
app_publisher = "KCSC"
app_description = "MASAR KSA HRMS"
app_email = "info@kcsc.com.jo"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/masar_ksa_hrms/css/masar_ksa_hrms.css"
# app_include_js = "/assets/masar_ksa_hrms/js/masar_ksa_hrms.js"

# include js, css files in header of web template
# web_include_css = "/assets/masar_ksa_hrms/css/masar_ksa_hrms.css"
# web_include_js = "/assets/masar_ksa_hrms/js/masar_ksa_hrms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "masar_ksa_hrms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "masar_ksa_hrms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "masar_ksa_hrms.utils.jinja_methods",
# 	"filters": "masar_ksa_hrms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "masar_ksa_hrms.install.before_install"
# after_install = "masar_ksa_hrms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "masar_ksa_hrms.uninstall.before_uninstall"
# after_uninstall = "masar_ksa_hrms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "masar_ksa_hrms.utils.before_app_install"
# after_app_install = "masar_ksa_hrms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "masar_ksa_hrms.utils.before_app_uninstall"
# after_app_uninstall = "masar_ksa_hrms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "masar_ksa_hrms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Salary Component": {
		"validate": "masar_ksa_hrms.custom.salary_component.salary_component.validate",
	} ,
    "Employee" : { 
        "validate":"masar_ksa_hrms.custom.employee.employee.validate",
    },
    "Shift Type" : {
        "validate":"masar_ksa_hrms.custom.shift_type.shift_type.validate",
    },
    "Company":{
        "validate":"masar_ksa_hrms.custom.company.company.validate",
    }
}
doctype_js = {
    "Employee": "custom/employee/employee.js"
}
doctype_list_js = {
    "Attendance Shortage" : "masar_ksa_hrms/doctype/attendance_shortage/attendance_shortage_list.js"
    }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"masar_ksa_hrms.tasks.all"
# 	],
# 	"daily": [
# 		"masar_ksa_hrms.tasks.daily"
# 	],
# 	"hourly": [
# 		"masar_ksa_hrms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"masar_ksa_hrms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"masar_ksa_hrms.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "masar_ksa_hrms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "masar_ksa_hrms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "masar_ksa_hrms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["masar_ksa_hrms.utils.before_request"]
# after_request = ["masar_ksa_hrms.utils.after_request"]

# Job Events
# ----------
# before_job = ["masar_ksa_hrms.utils.before_job"]
# after_job = ["masar_ksa_hrms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"masar_ksa_hrms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "name", "in", [
                "Salary Component-custom_is_overtime_applicable", 
                "Salary Component-custom_formula_check",
                "Salary Component-custom_is_ss_applicable",
                "Salary Component-custom_salary_deduction",
                "Salary Component-custom_is_eos_applicable",
                "Employee-custom_nationality",
                "Employee-custom_overtime_details",
                "Employee-custom_is_overtime_applicable",
                "Employee-custom_salary_components", 
                "Employee-custom_employee_salary_component",
                "Employee-custom_social_security_details", 
                "Employee-custom__is_ss_applicable",
                "Employee-custom_ss_number",
                "Employee-custom_nationality_number" ,
                "Employee-custom_citizen_number",
                "Employee-custom_salaries" , 
                "Employee-custom_basic_salary" ,
                "Employee-custom_salary_deduction",
                "Employee-custom_column_break_xom87",
                "Employee-custom_basic_salary_with_allowance",
                "Employee-custom_eos_salary",
                "Shift Assignment-custom_employee_shift_management",
                "Company-custom_end_of_service_info",
                "Company-custom_comp_eos_table",
                "Company-custom_end_of_service_accounts",
                "Company-custom_end_of_service_expenses",
                "Company-custom_column_break_udaic",
                "Company-custom_end_of_service_liabilities",
                "Company-custom_salary", 
                "Company-custom_social_security_info" , 
                "Company-custom_salary_component" , 
                "Company-custom_social_security_info", 
                "Company-custom_saudi_arabia_info", 
                "Company-custom_comp_ss_sa_rate", 
                "Company-custom_emp_ss_sa_rate", 
                "Company-custom_column_break_62qlj", 
                "Company-custom_other_nationality_info", 
                "Company-custom_comp_ss_other_rate", 
                "Company-custom_emp_ss_other_rate", 
                "Company-custom_emp_ss_other_rate", 
                "Company-custom_ss_expenses", 
                "Company-custom_column_break_syuvv", 
                "Company-custom_ss_liabilities", 
                "Shift Type-custom_grace_period_settings_overtime_section",
                "Shift Type-custom_enable_early_entry_marking" , 
                "Shift Type-custom_early_entry_grace_period",
                "Shift Type-custom_column_break_wzcol", 
                "Shift Type-custom_enable_late_exit_marking",
                "Shift Type-custom_late_exit_grace_period",
                # "Shift Type-custom_30_working_day",
                "Attendance-custom_att_pro_ref",
                "Leave Type-custom_salary_deduction",
                "Leave Type-custom_balance_deduction",
                "Leave Type-custom_salary_deduction_rate", 
                "Leave Application-custom_sla_reference"
                ]
        ]
    ]},
    {"dt": "Payroll Settings", "filters": [
            {
                "doctype": "Payroll Settings", 
                "value": 0, 
                "fieldname": "working_day_30" ,
                "fieldtype": "Check", 
                "label": "Working Day 30"
            }
    ]}

]