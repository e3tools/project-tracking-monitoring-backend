// Copyright (c) 2025, Steve Nyaga and contributors
// For license information, please see license.txt
frappe.provide("project_monitor.projects");
frappe.ui.form.on("Project Ex", {
  setup(frm) {
    frm.set_query("admin_level", "administrative_areas", function () {
      return {
        filters: {
          name: frm.doc.administrative_level,
        },
      };
    });
  },
  refresh(frm) {},
  administrative_level(frm) {
    frappe.model.set_value(frm.doctype, frm.docname, "project_location", null);
    frm.clear_table("administrative_areas");
    frm.refresh_fields();
    // loop through the items and set the admin level
    (frm.doc.administrative_areas || []).forEach((item) => {
      frappe.model.set_value(
        item.doctype,
        item.name,
        "admin_level",
        frm.doc.administrative_level
      );
    });
  },
});

frappe.ui.form.on("Project Location Item Ex", {
  administrative_areas_add(frm, cdt, cdn) {
    if (frm.doc.administrative_level) {
      var row = frappe.get_doc(cdt, cdn);
      row.admin_level = frm.doc.administrative_level;
      frm.refresh_field("administrative_areas", cdn, "admin_level");
    }
  },
  administrative_areas_remove(frm, cdt, cdn) {
    project_monitor.projects.load_maps(frm);
  },
  admin(frm, cdt, cdn) {
    console.log("Admin changed");
    project_monitor.projects.load_maps(frm);
  },
});

project_monitor.projects.load_maps = (frm) => {
  frappe.model.set_value(frm.doctype, frm.docname, "project_location", null);
  frm.doc.administrative_areas.forEach((el) => {
    frappe.call({
      doc: frm.doc,
      method: "get_vector",
      args: {
        doctype: el.admin_level,
        docname: el.admin,
      },
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(
            frm.doctype,
            frm.docname,
            "project_location",
            r.message
          );
        }
      },
    });
  });
};
