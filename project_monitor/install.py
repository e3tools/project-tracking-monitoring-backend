import frappe
import os
from frappe import get_app_path
from frappe.utils.file_manager import save_file


def after_install():
    # set default content
    setup_default_cover_image()
    setup_default_admin_level_names()
    return
    # Automatically configure CORS for the site on app installation
    frappe.installer.update_site_config("allow_cors", "*")  # or "http://localhost:3000"
    frappe.installer.update_site_config(
        "allow_cors_methods", "GET, POST, PUT, DELETE, OPTIONS"
    )
    frappe.installer.update_site_config(
        "allow_cors_headers", "Authorization, Content-Type, Cookie, X-Frappe-Site-Name"
    )


def setup_default_cover_image():
    # 1. Path to local image inside the app directory
    image_path = get_app_path(
        "project_monitor", "public", "images", "default_project_cover.png"
    )

    if not os.path.exists(image_path):
        frappe.log_error(
            "Default cover image not found in public folder", "App Setup Error"
        )
        return

    # 2. Get Single DocType for Settings
    settings_doc = "Project Monitor Settings"

    # Check if image is already attached to avoid duplicate uploads
    current_image = frappe.db.get_single_value(settings_doc, "default_cover_image")
    if current_image:
        return

    # 3. Read image content
    with open(image_path, "rb") as f:
        content = f.read()

    # 4. Save file into Frappe File Manager and attach to Single DocType
    saved_file = save_file(
        fname="default_project_cover.jpg",
        content=content,
        dt=settings_doc,
        dn=settings_doc,
        is_private=0,  # Set to 0 so public frontend portals can render it
    )

    # 5. Assign file URL to the default_cover_image field
    frappe.db.set_single_value(settings_doc, "default_cover_image", saved_file.file_url)


def setup_default_admin_level_names():
    settings_doc = "Project Monitor Settings"
    frappe.db.set_single_value(
        settings_doc,
        "pending_bill_calculation_method",
        "Earned Value Progress Estimate",
    )
    frappe.db.set_single_value(settings_doc, "admin_1_display_name", "County")
    frappe.db.set_single_value(settings_doc, "admin_2_display_name", "Sub County")
    frappe.db.set_single_value(settings_doc, "admin_3_display_name", "Ward")
    frappe.db.set_single_value(settings_doc, "admin_4_display_name", "Location")
