# Copyright (c) 2025, Steve Nyaga and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProjectXTeam(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from project_monitor.project_monitor.doctype.projectx_team_member.projectx_team_member import ProjectXTeamMember

		members: DF.Table[ProjectXTeamMember]
		project: DF.Link | None
		project_location: DF.ReadOnly | None
		project_name: DF.ReadOnly | None
		project_status: DF.ReadOnly | None
	# end: auto-generated types
	pass
