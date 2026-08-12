// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("ProjectX Post Evaluation", {
  refresh(frm) {},
  project: function (frm) {
    if (!frm.doc.project) return;

    // Load historical metrics from ProjectX
    frappe.db
      .get_value("ProjectX", frm.doc.project, [
        "approved_budget",
        "total_expenditure_amount",
        "expected_end_date",
        "current_physical_progress",
      ])
      .then((r) => {
        if (r && r.message) {
          const budget = flt(r.message.approved_budget);
          const expenditure = flt(r.message.total_expenditure_amount);
          const plannedEnd = r.message.expected_end_date;

          frm.set_value("approved_budget", budget);
          frm.set_value("final_expenditure", expenditure);
          frm.set_value("cost_variance", budget - expenditure);
          frm.set_value("planned_end_date", plannedEnd);

          frm.trigger("calculate_schedule_variance");
        }
      });
  },

  actual_completion_date: function (frm) {
    frm.trigger("calculate_schedule_variance");
  },

  calculate_schedule_variance: function (frm) {
    if (frm.doc.planned_end_date && frm.doc.actual_completion_date) {
      const diff = frappe.datetime.date_diff(
        frm.doc.actual_completion_date,
        frm.doc.planned_end_date,
      );
      frm.set_value("schedule_variance_days", diff);
    }
  },
});
