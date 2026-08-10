window.project_monitor = window.project_monitor || {};

project_monitor.report_utils = {
  set_report_filter_hint: function (fieldname, text) {
    const field = frappe.query_report.get_filter(fieldname);

    if (!field) return;

    field.$input.attr("placeholder", text);
    field.$wrapper.attr("data-original-title", text);
    field.$wrapper.find(".tooltip-content").text(text);
  },
};
