// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.query_reports["Project Health And Exception Report"] = {
  filters: [
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "DepartmentX",
    },
    {
      fieldname: "health_status",
      label: __("Health Category"),
      fieldtype: "Select",
      options:
        "\nCritical / Action Required\nDelayed\nBudget Exceeded\nOn Track",
    },
    {
      fieldname: "exception_type",
      label: __("Filter by Specific Exception"),
      fieldtype: "Select",
      options:
        "\nAll Exceptions\nOver Budget\nProgress Lag (>15% gap)\nStale Progress (>60 days)\nHigh Pending Liabilities (> budget)",
    },
  ],
};
