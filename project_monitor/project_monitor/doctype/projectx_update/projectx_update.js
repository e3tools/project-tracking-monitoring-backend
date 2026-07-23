// Copyright (c) 2025, Steve Nyaga and contributors
// For license information, please see license.txt
cur_frm.add_fetch(
  "project_update_type",
  "is_updating_project_progress",
  "is_project_progress",
);
frappe.ui.form.on("ProjectX Update", {
  refresh(frm) {},
});
