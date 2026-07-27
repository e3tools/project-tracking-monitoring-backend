import frappe


def after_install():
    # Automatically configure CORS for the site on app installation
    frappe.installer.update_site_config("allow_cors", "*")  # or "http://localhost:3000"
