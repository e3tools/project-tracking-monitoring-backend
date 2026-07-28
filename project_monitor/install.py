import frappe


def after_install():
    # Automatically configure CORS for the site on app installation
    frappe.installer.update_site_config("allow_cors", "*")  # or "http://localhost:3000"
    frappe.installer.update_site_config(
        "allow_cors_methods", "GET, POST, PUT, DELETE, OPTIONS"
    )
    frappe.installer.update_site_config(
        "allow_cors_headers", "Authorization, Content-Type, Cookie, X-Frappe-Site-Name"
    )
