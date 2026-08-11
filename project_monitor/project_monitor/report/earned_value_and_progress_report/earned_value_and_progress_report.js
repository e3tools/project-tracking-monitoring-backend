// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.query_reports["Earned Value And Progress Report"] = {
  filters: [
    {
      fieldname: "project",
      label: __("Project"),
      fieldtype: "Link",
      options: "ProjectX",
    },
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "DepartmentX",
    },
    {
      fieldname: "admin_2",
      label: __("Sub County"),
      fieldtype: "Link",
      options: "Admin 2",
    },
    {
      fieldname: "status",
      label: __("Project Status"),
      fieldtype: "Link",
      options: "ProjectX Status",
    },
  ],
  onload: function (report) {
    Promise.all([
      frappe.db.get_single_value(
        "Project Monitor Settings",
        "admin_2_display_name",
      ),
      frappe.db.get_single_value(
        "Project Monitor Settings",
        "admin_3_display_name",
      ),
    ]).then(([admin2, admin3]) => {
      if (admin2) {
        project_monitor.report_utils.set_report_filter_hint("admin_2", admin2);
      }

      if (admin3) {
        project_monitor.report_utils.set_report_filter_hint("admin_3", admin3);
      }
    });
  },
};
