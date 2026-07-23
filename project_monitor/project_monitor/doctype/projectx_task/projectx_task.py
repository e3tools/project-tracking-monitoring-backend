# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet


class ProjectXTask(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_end_date: DF.Date | None
		actual_start_date: DF.Date | None
		expected_end_date: DF.Date | None
		expected_start_date: DF.Date | None
		is_group: DF.Check
		lft: DF.Int
		old_parent: DF.Link | None
		parent_taskx: DF.Link | None
		project: DF.Link | None
		rgt: DF.Int
		status: DF.Literal["Open", "In Progress", "Overdue", "Completed", "Cancelled"]
		task_name: DF.Data
		task_type: DF.Link | None
		task_weight: DF.Int
		total_cost: DF.Currency
	# end: auto-generated types
	pass
