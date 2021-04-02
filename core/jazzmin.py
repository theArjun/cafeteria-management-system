JAZZMIN_SETTINGS = {

    # title of the window
    "site_title": "Cafeteria Management System",

    # Title on the brand, and the login screen (19 chars max)
    "site_header": "Cafeteria MS",

    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "/logo/cafems.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Cafeteria Admin",

    # Copyright on the footer
    "copyright": "Arjun Adhikari",

    # Field name on user model that contains avatar image
    "user_avatar": None,

    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "cafeteria.customer",

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["cafeteria",],

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free
    # for a list of icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "admin.LogEntry": "fas fa-file-alt",
        "cafeteria.dailybalance": "fas fa-file-invoice-dollar",
        "cafeteria.expense": "fas fa-coins",
        "cafeteria.income": "fas fa-dollar-sign",
        "cafeteria.particular": "fas fa-pizza-slice",
        "cafeteria.penalty": "fas fa-user-minus",
        "cafeteria.stock": "fas fa-layer-group",
        "cafeteria.transaction": "fas fa-hand-holding-usd",
        "cafeteria.cafeteriamanager": "fas fa-user-circle",
        "cafeteria.customer":"fas fa-users"
    },

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "collapsible",

    "show_ui_builder": True,

}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-warning",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "cosmo",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}
