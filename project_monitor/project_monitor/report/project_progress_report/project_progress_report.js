// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Report"] = {
  filters: [
    {
      fieldname: "project",
      label: __("Project"),
      fieldtype: "Link",
      options: "ProjectX",
    },
    {
      fieldname: "from_date",
      label: __("From Inspection Date"),
      fieldtype: "Date",
    },
    {
      fieldname: "to_date",
      label: __("To Inspection Date"),
      fieldtype: "Date",
    },
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "DepartmentX",
    },
  ],
};
