# Copyright (c) 2026, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectMonitorSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		admin_1_display_name: DF.Data | None
		admin_2_display_name: DF.Data | None
		admin_3_display_name: DF.Data | None
		admin_4_display_name: DF.Data | None
		pending_bill_calculation_method: DF.Literal["Payment Certificate (IPC) Ledger", "Earned Value Progress Estimate"]
	# end: auto-generated types
	pass
