import frappe
from frappe import _
from masar_ksa_hrms.masar_ksa_hrms.doctype.utils import eos_validation

def validate(self, method):
   eos_validation(self ,table_name = 'custom_comp_eos_table' , rate_name = 'salary_rate')