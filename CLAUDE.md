# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cosmetic expiry tracking application built with Django. Users can register cosmetic products with their opening dates and automatically receive expiry calculations and notifications. The app integrates LLM (OpenAI API) to auto-suggest categories and provide hygiene risk assessments and usage improvement advice.

**Key Features:**
- Hierarchical product categorization system (Taxon model)
- Automatic expiry date calculation based on product type
- Notification system for expiring products
- LLM integration for smart category suggestions
- User authentication and product management
- Responsive web interface with Bootstrap

## Development Commands

### Django Management Commands

```bash
# Start development server
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate

# Admin operations
python manage.py createsuperuser

# Development utilities
python manage.py check
python manage.py test
python manage.py shell
python manage.py collectstatic

# Run specific app tests
python manage.py test beauty

# Generate notifications (scheduled task)
python manage.py generate_notifications
```

### Virtual Environment

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate requirements file after installing new packages
pip freeze > requirements.txt
```

### Database Management

```bash
# Reset database (development only)
python manage.py flush

# Create superuser for admin access
python manage.py createsuperuser

# Database shell access
python manage.py dbshell
```

### Environment Variables Setup

The project uses dotenv for environment variables:

```bash
# Create .env file in project root (if not exists)
touch .env

# Add OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

### Utility Scripts

The project includes several utility scripts that can be run directly with Python:

```bash
# Initialize taxon hierarchy for product categories
python init_taxons.py

# List all taxons in the system
python list_taxons.py

# List all users in the system
python list_users.py

# Create sample items for testing
python create_sample_items.py

# Generate notifications for existing items
python create_notifications.py
```

## Project Architecture Overview

### Core Models (`beauty/models.py`)

1. **BaseModel**: Abstract base with timestamps
   - Provides `created_at` and `updated_at` fields to all models

2. **Taxon**: Hierarchical category system
   - Self-referencing tree structure for cosmetic categories
   - Auto-calculates `depth` and `full_path` on save
   - `is_leaf` property determines if category can be assigned to items
   - Includes shelf life configuration (months and anchor type)

3. **Item**: Main product entity
   - User ownership enforced via ForeignKey with CASCADE deletion
   - Uses Taxon for hierarchical categorization via `product_type` field
   - Tracks opening date, expiry date, and status ('using'/'finished')
   - Risk assessment levels ('low'/'mid'/'high') for expiry alerts
   - Properties: `main_category`, `middle_category` for navigation breadcrumbs

4. **Notification**: Automated alert system
   - Types: 30-day, 14-day, 7-day warnings, and overdue alerts
   - Links to User and Item with CASCADE deletion
   - Scheduled notification system with read status tracking

5. **LlmSuggestionLog**: AI integration tracking
   - Records LLM suggestions vs user choices for learning
   - Links both suggested and chosen taxons for analysis
   - Tracks suggestion acceptance rate by target type

### Authentication System

Email-based authentication instead of username:
- Custom `EmailBackend` (`beauty/backends.py`)
- `SignUpForm` with email validation and password strength checks
- `SignInView` with email lookup for login authentication
- All item operations require login and enforce user ownership for security

### Frontend Architecture

- Bootstrap 5.2.3 for responsive design
- Chart.js for statistics dashboard
- Custom JavaScript for dynamic filtering and AJAX loading
- Hierarchical category filtering with dynamic selects

### Notification System

- Custom management command (`generate_notifications.py`) for scheduled notifications
- Transaction-based atomic creation of notifications
- API endpoints for notification summary and status updates

### LLM Integration

- OpenAI API integration for category suggestions
- Structured JSON response format
- Suggestion logging system for performance tracking

## Security Patterns

All item views follow this security pattern:
```python
try:
    item = Item.objects.get(id=id, user=request.user)
except Item.DoesNotExist:
    other_user_item = Item.objects.filter(id=id).first()
    if other_user_item:
        raise PermissionDenied("権限なし")
    else:
        raise Http404("見つかりません")
```

## Configuration Details

- **Language**: Japanese (`ja`) with Asia/Tokyo timezone
- **Database**: SQLite for development
- **Static Files**: Served from `beauty/static/`
- **Media Files**: User uploads stored in `media/` directory
- **Environment Variables**: Uses python-dotenv for OPENAI_API_KEY

## Development Environment

- **Python**: 3.13+
- **Django**: 5.2.4
- **Frontend**: Bootstrap 5.2.3, Font Awesome 6.0.0, Chart.js
- **Database**: SQLite (development)
- **Image Processing**: Pillow>=11.3.0

## Testing and Quality Assurance

No formal testing framework is currently configured, but standard Django tests can be run:
- Use `python manage.py test` for running tests
- Use `python manage.py test beauty` for app-specific tests