from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("product_view/<int:myid>/", views.product_view, name="product_view"),
    path("search/", views.search, name="search"),
    path("tracker/", views.tracker, name="tracker"),
    path("contact/", views.contact, name="contact"),
    path("loggedin_contact/", views.loggedin_contact, name="loggedin_contact"),

    path("register/", views.register, name="register"),
    path("change_password/", views.change_password, name="change_password"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add_wishlist/<int:myid>/", views.add_wishlist, name="add_wishlist"),
    path("profile/", views.profile, name="profile"),
    
    # Seller Panel Routes
    path("seller_signup/", views.seller_signup, name="seller_signup"),
    path("seller_dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller_products/", views.seller_products, name="seller_products"),
    path("seller_add_product/", views.seller_add_product, name="seller_add_product"),
    path("seller_edit_product/<int:product_id>/", views.seller_edit_product, name="seller_edit_product"),
    path("seller_delete_product/<int:product_id>/", views.seller_delete_product, name="seller_delete_product"),
    path("seller_orders/", views.seller_orders, name="seller_orders"),
    path("seller_analytics/", views.seller_analytics, name="seller_analytics"),
    path("seller_reviews/", views.seller_reviews, name="seller_reviews"),
    path("seller_inventory/", views.seller_inventory, name="seller_inventory"),
    path("update_stock/<int:product_id>/", views.update_stock, name="update_stock"),
    path("seller_settings/", views.seller_settings, name="seller_settings"),
    path("seller_restore_products/", views.seller_restore_products, name="seller_restore_products"),
    path("seller_restore_action/<int:product_id>/", views.seller_restore_action, name="seller_restore_action"),
    path("seller_order_details/<int:order_id>/", views.seller_order_details, name="seller_order_details"),
    path("update_order_status/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("seller_analytics_data/", views.seller_analytics_data, name="seller_analytics_data"),
    
    # Admin Panel Routes
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("approve_seller/<int:seller_id>/", views.approve_seller, name="approve_seller"),
    path("reject_seller/<int:seller_id>/", views.reject_seller, name="reject_seller"),
    
    # Placeholders & New Features
    path("settings/", views.seller_settings, name="settings"),
    path("notifications/", views.notifications, name="notifications"),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("ajax_search/", views.ajax_search, name="ajax_search"),
    
    path("about/", lambda r: views.generic_placeholder(r, 'About Us'), name="about"),
    path("faq/", lambda r: views.generic_placeholder(r, 'FAQ'), name="faq"),
    path("terms/", lambda r: views.generic_placeholder(r, 'Terms & Conditions'), name="terms"),
    path("privacy/", lambda r: views.generic_placeholder(r, 'Privacy Policy'), name="privacy"),
    path("returns/", lambda r: views.generic_placeholder(r, 'Returns & Refunds'), name="returns"),
    path("careers/", lambda r: views.generic_placeholder(r, 'Careers'), name="careers"),
    path("blog/", lambda r: views.generic_placeholder(r, 'Blog'), name="blog"),
    path("deals/", lambda r: views.generic_placeholder(r, 'Deals'), name="deals"),
    path("prime/", lambda r: views.generic_placeholder(r, 'Shopvexael Prime'), name="prime"),
]