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
    
    # Placeholders for Shopvexael V2 Expansion
    path("settings/", lambda r: views.generic_placeholder(r, 'Settings'), name="settings"),
    path("notifications/", lambda r: views.generic_placeholder(r, 'Notifications'), name="notifications"),
    path("seller_dashboard/", lambda r: views.generic_placeholder(r, 'Seller Dashboard'), name="seller_dashboard"),
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