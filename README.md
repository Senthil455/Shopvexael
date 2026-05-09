# Shopvexael — Premium Multi-Vendor Marketplace

Shopvexael is a professional, high-performance eCommerce platform built with Django. It features a modern, glassmorphic dark-mode interface and a robust multi-vendor architecture, providing a seamless experience for customers, sellers, and administrators.

![Banner](https://img.shields.io/badge/Shopvexael-Production--Ready-gold?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-6.0+-092e20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.14+-3776ab?style=for-the-badge&logo=python)

## 🚀 Key Features

### 🛒 Customer Experience
- **Premium UI/UX**: Dark-mode glassmorphic design with smooth micro-animations.
- **Smart Search**: AJAX-powered real-time search with instant suggestions.
- **Order Tracking**: Animated tracking timeline with real-time status updates.
- **Social Features**: Detailed product reviews with helpfulness ratings and seller replies.
- **Shopping Essentials**: Dynamic cart management, wishlists, and multi-payment support.

### 🏪 Seller Hub (Enterprise Grade)
- **Advanced Analytics**: Real-time sales visualization using Chart.js.
- **Inventory Management**: Health indicators, quick stock updates, and a "Trash Bin" for soft-deleted products.
- **Order Fulfillment**: Dedicated dashboard for tracking shipments, updating statuses, and generating invoices.
- **Communication**: Integrated notification center for order alerts and platform updates.

### 🛡️ Admin Command Center
- **Platform Analytics**: Total revenue tracking and automatic commission calculation (10%).
- **Verification Queue**: Dedicated workflow for vetting and approving/rejecting new seller applications.
- **Global Control**: Full management of categories, brands, and featured/trending product listings.

## 🛠️ Technical Stack
- **Backend**: Django 6.0 (Python)
- **Frontend**: Vanilla CSS (Custom Design System), JavaScript (AJAX/DOM)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Analytics**: Chart.js
- **Icons**: FontAwesome 5

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Senthil455/Shopvexael.git
   cd online-shopping-python-project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install django
   ```

4. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create an Admin (Superuser)**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**:
   ```bash
   python manage.py runserver
   ```

## 📂 Project Structure
- `shop/`: Core application containing models, views, and business logic.
- `OnlineShopping/`: Project configuration (settings, master URLs).
- `static/`: Global CSS, JavaScript, and asset files.
- `media/`: User-uploaded product images and seller documents.
- `templates/`: Modular HTML components with advanced layout inheritance.

## 🔐 Admin Credentials (Demo)
If you are testing the local development environment:
- **URL**: `/admin_dashboard/`
- **Username**: `admin`
- **Password**: `adminpassword`

---
Developed with ❤️ by [Antigravity](https://github.com/Antigravity-AI) for **Shopvexael Enterprise**.
