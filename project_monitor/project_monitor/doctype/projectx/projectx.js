// Copyright (c) 2025, Steve Nyaga and contributors
// For license information, please see license.txt
frappe.provide("project_monitor.projects");
frappe.ui.form.on("ProjectX", {
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
        frm.doc.administrative_level,
      );
    });
  },
  project_location(frm) {
    if (!frm.doc.project_location) {
      frappe.model.set_value(frm.doc.doctype, frm.doc.name, "latitude", 0);
      frappe.model.set_value(frm.doc.doctype, frm.doc.name, "longitude", 0);
      return;
    }

    const geojson = JSON.parse(frm.doc.project_location);

    if (
      geojson.features &&
      geojson.features.length > 0 &&
      geojson.features[0].geometry.type === "Point"
    ) {
      const [lng, lat] = geojson.features[0].geometry.coordinates;
      frappe.model.set_value(frm.doc.doctype, frm.doc.name, "latitude", lat);
      frappe.model.set_value(frm.doc.doctype, frm.doc.name, "longitude", lng);
      console.log("Latitude:", lat);
      console.log("Longitude:", lng);
    }
    // const geo = frm.fields_dict.project_location.map;

    // if (!geo) return;

    // // Leaflet map instance
    // const map = geo.map;

    // map.eachLayer(function (layer) {
    //   if (layer instanceof L.Marker) {
    //     layer.on("click", function (e) {
    //       debugger;
    //       console.log("Latitude:", e.latlng.lat);
    //       console.log("Longitude:", e.latlng.lng);
    //     });
    //   }
    // });
  },
});

frappe.ui.form.on("ProjectX Location Item", {
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
            r.message,
          );
        }
      },
    });
  });
};

// Set total payment amount
frappe.ui.form.on(
  "ProjectX Funding Source",
  "percentage_of_funding",
  function (frm) {
    project_monitor.projects.set_total_funding(frm);
  },
);

frappe.ui.form.on(
  "ProjectX Funding Source",
  "source_of_funds_remove",
  function (frm) {
    project_monitor.projects.set_total_funding(frm);
  },
);

project_monitor.projects.set_total_funding = function (frm) {
  var total = 0.0;
  $.each(frm.doc.source_of_funds || [], function (i, row) {
    if (row.percentage_of_funding) {
      total = total + row.percentage_of_funding;
    } else {
      if (row.percentage_of_funding < 0) {
        msgprint(
          __("Row {0}: Percentage of funding cannot be negative", [row.idx]),
        );
        frappe.model.set_value(
          row.doctype,
          row.name,
          "percentage_of_funding",
          0.0,
        );
      }
    }
  });
  frm.set_value("total_percentage", total);
};
