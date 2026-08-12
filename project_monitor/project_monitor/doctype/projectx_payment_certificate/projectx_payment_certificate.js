// Copyright (c) 2026, Steve Nyaga and contributors
// For license information, please see license.txt

frappe.ui.form.on("ProjectX Payment Certificate", {
  refresh(frm) {},
  gross_certified_amount: function (frm) {
    frm.trigger("calculate_net_payable");
  },
  retention_amount: function (frm) {
    frm.trigger("calculate_net_payable");
  },
  calculate_net_payable: function (frm) {
    let gross = flt(frm.doc.gross_certified_amount);
    let retention = flt(frm.doc.retention_amount);

    if (retention > gross) {
      frappe.msgprint(
        __("Retention amount cannot exceed gross certified amount."),
      );
      frm.set_value("retention_amount", 0);
      retention = 0;
    }

    frm.set_value("net_payable_amount", gross - retention);
  },
});
