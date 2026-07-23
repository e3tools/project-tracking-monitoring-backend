// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

cur_frm.add_fetch("feedback", "project", "project");
cur_frm.add_fetch("feedback", "is_public", "is_public");
frappe.ui.form.on("ProjectX Feedback Response", {
  refresh(frm) {},
});
