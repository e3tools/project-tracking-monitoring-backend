frappe.router.on("change", () => {
  // Inject styles ONLY when on the Project Monitor workspace
  if (
    frappe.get_route()[0] === "workspaces" &&
    frappe.get_route()[1] === "project-monitor"
  ) {
    inject_workspace_styles();
  }
});

function inject_workspace_styles() {
  if (document.getElementById("project-monitor-style")) return;

  const style = document.createElement("style");
  style.id = "project-monitor-style";
  style.innerHTML = `
        /* Applied only to rendered workspace cards */
        .workspace-page .widget-box,
        .workspace-page .widget {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .workspace-page .widget-box:hover,
        .workspace-page .widget:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .workspace-page .widget.number-card-widget {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        }
    `;
  document.head.appendChild(style);
}
