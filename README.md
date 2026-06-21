# Shopvexael — Multi-Vendor Marketplace

Shopvexael is an eCommerce platform built with Django. It features a modern dark-mode interface and multi-vendor architecture for customers, sellers, and administrators.

![Django](https://img.shields.io/badge/Django-5.2-092e20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python)

## Features

### Customer Experience
- Premium dark-mode UI with glassmorphic design
- AJAX-powered real-time search with suggestions
- Order tracking with timeline and status updates
- Product reviews with ratings and seller replies
- Cart management, wishlists, and multiple payment methods

### Seller Hub
- Sales analytics with Chart.js visualizations
- Inventory management with stock health indicators
- Order fulfillment with status tracking
- Product management with soft-delete and restore

### Admin Panel
- Platform analytics and revenue tracking
- Seller verification and approval workflow
- Category, brand, and product management

## Requirements

- Python 3.11+
- Django 5.2
- See `requirements.txt` for full list

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Senthil455/Shopvexael.git
   cd Shopvexael
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
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

## Environment Variables

Create a `.env` file or set these environment variables:

| Variable | Description | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required in production) | Auto-generated in dev |
| `DJANGO_DEBUG` | Enable debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection string (production) | SQLite (dev) |
| `DJANGO_DEFAULT_FROM_EMAIL` | Sender email address | `noreply@shopvexael.com` |
| `DJANGO_EMAIL_BACKEND` | Email backend | Console (dev) |

## Project Structure

- `shop/`: Core application (models, views, templates)
- `OnlineShopping/`: Project configuration (settings, URLs)
- `static/`: Global CSS, JavaScript, assets
- `media/`: User-uploaded images

## Deployment

The project includes a `netlify.toml` for serverless deployment on Netlify with `gunicorn` as the WSGI server. Set the required environment variables in your hosting dashboard.
