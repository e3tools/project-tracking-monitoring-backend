from frappe import _


def get_data():
    return {
        "fieldname": "feedback",
        # "non_standard_fieldnames": {
        #     "Item": "default_bom",
        #     "Purchase Order": "bom",
        #     "Purchase Receipt": "bom",
        #     "Purchase Invoice": "bom",
        # },
        "transactions": [
            {
                "label": _("Feedback Responses"),
                "items": ["Item", "ProjectX Feedback Response"],
            },
        ],
        # "disable_create_buttons": [
        # 	"Item",
        # 	"Purchase Order",
        # 	"Purchase Receipt",
        # 	"Purchase Invoice",
        # 	"Job Card",
        # 	"Stock Entry",
        # 	"BOM",
        # ],
    }
