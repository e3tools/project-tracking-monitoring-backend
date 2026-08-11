// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.query_reports["Ward & Sub-County Project Matrix"] = {
  filters: [
    {
      fieldname: "admin_2",
      label: __("Sub-County"),
      fieldtype: "Link",
      options: "Admin 2",
    },
    {
      fieldname: "admin_3",
      label: __("Ward"),
      fieldtype: "Link",
      options: "Admin 3",
    },
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "DepartmentX",
    },
    {
      fieldname: "status",
      label: __("Project Status"),
      fieldtype: "Link",
      options: "ProjectX Status",
    },
  ],

  onload: function (report) {
    // Fetch display names dynamically from Project Monitor Settings
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
    // frappe.db
    //   .get_value("Project Monitor Settings", "Project Monitor Settings", [
    //     "admin_2_display_name",
    //     "admin_3_display_name",
    //   ])
    //   .then((r) => {
    //     if (r && r.message) {
    //       const admin1 = r.message.admin_2_display_name;
    //       const admin2 = r.message.admin_3_display_name;

    //       if (admin1) {
    //         const subCountyFilter = report.get_filter("admin_2");
    //         if (subCountyFilter) {
    //           subCountyFilter.df.label = __(admin1);
    //           subCountyFilter.refresh();
    //         }
    //       }

    //       if (admin2) {
    //         const wardFilter = report.get_filter("admin_2");
    //         if (wardFilter) {
    //           wardFilter.df.label = __(admin2);
    //           wardFilter.refresh();
    //         }
    //       }
    //     }
    //   });
  },
};
