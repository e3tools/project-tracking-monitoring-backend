// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.query_reports["Ward And Sub County Project Matrix"] = {
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
};
