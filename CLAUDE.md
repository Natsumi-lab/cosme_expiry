# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cosmetic expiry tracking application built with Django. Users can register cosmetic products with their opening dates and automatically receive expiry calculations and notifications. The app integrates LLM (ChatGPT API) to auto-suggest categories and provide hygiene risk assessments and usage improvement advice. This project serves as a portfolio demonstrating practical design, implementation, and frontend skills.

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
```

### Database Management

```bash
# Check migration status
python manage.py showmigrations

# Create migrations for specific app
python manage.py makemigrations beauty

# Apply specific migrations
python manage.py migrate beauty
```

### Virtual Environment

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies (no requirements.txt yet)
pip install Django==5.2.4

# Generate requirements file after installations
pip freeze > requirements.txt
```

## Architecture Overview

### Project Structure

Single Django app architecture:
- **Main Project**: `cosme_expiry_app/` - Settings, main URLs, WSGI/ASGI configuration
- **Beauty App**: `beauty/` - Contains all business logic

### Core Models Architecture

The data model is built around four main entities:

1. **Taxon** (`beauty/models.py:14-49`): Hierarchical category system
   - Self-referencing tree structure for cosmetic categories
   - Auto-calculates `depth` and `full_path` on save
   - `is_leaf` property determines if category can be assigned to items
   - Used for organizing products (e.g., Makeup > Lips > Lip Gloss)

2. **Item** (`beauty/models.py:52-127`): Main product entity
   - Links to User via ForeignKey
   - Uses Taxon for hierarchical categorization
   - Tracks opening date, expiry date, and status ('using'/'finished')
   - Risk assessment levels ('low'/'mid'/'high') for alerts
   - Properties: `main_category`, `middle_category` for navigation

3. **Notification** (`beauty/models.py:130-153`): Automated alert system
   - Links to User and Item
   - Types: 30-day, 14-day, 7-day warnings, and overdue alerts
   - Scheduled notification system with read status tracking

4. **LlmSuggestionLog** (`beauty/models.py:156-201`): AI integration tracking
   - Records LLM suggestions vs user choices for learning
   - Tracks category, product name, and brand suggestions
   - Links both suggested and chosen taxons for analysis

### Admin Interface Configuration

Fully configured admin interface (`beauty/admin.py`) with:
- Custom filters and search fields for all models
- Taxon admin restricts Item.product_type to leaf nodes only
- Date hierarchy for notifications and items
- Advanced filtering by category hierarchy levels

### Frontend Architecture

**Template System** (`beauty/templates/`):
- `base.html`: Responsive Bootstrap layout with mobile-first design
- Navigation with offcanvas mobile menu
- Chart.js integration for statistics display
- Font Awesome icons throughout

**Static File Organization** (`beauty/static/`):
```
css/
├── styles.css          # Main styling
└── custom-styles.css   # Custom overrides
images/
├── favicon.ico
└── header.jpg
js/
└── scripts.js          # Main JavaScript
```

**Design System**:
- Primary: `#f8dec6` (Light Cream)
- Secondary: #f0d5bb
- Accent: `#d3859c` (Dusty Rose)
- Bootstrap 5.2.3 with responsive breakpoints

### LLM Integration Framework

**Current Implementation** (`beauty/views.py:68-106`):
- `process_llm_suggestion()`: Framework for LLM API calls
- `confirm_llm_suggestion()`: User confirmation handling
- Logs all AI suggestions and user selections for learning

## Configuration Details

### Settings (`cosme_expiry_app/settings.py`)

- **Language**: Japanese (`ja`) with Asia/Tokyo timezone
- **Database**: SQLite for development
- **Static Files**: Configured to serve from `beauty/static/`
- **Templates**: Located in `beauty/templates/`
- **Virtual Environment**: Uses `venv/` directory (not `myenv/`)

### URL Configuration

- Main URLs in `cosme_expiry_app/urls.py`
- App-specific URLs in `beauty/urls.py`
- Admin interface available at `/admin/`

## Development Environment

- **Python**: 3.13.5
- **Django**: 5.2.4
- **Frontend**: Bootstrap 5.2.3, Font Awesome 6.0.0, Chart.js
- **Database**: SQLite (development)
- **Virtual Environment**: `venv/` (Windows: `venv\Scripts\activate`)

## Implementation Status

**Completed:**
- Complete data model structure with migrations applied
- Fully functional admin interface with custom configurations
- LLM integration framework structure
- Responsive frontend templates with mobile support
- User registration system (`SignUpView` in `beauty/views.py:23-64`)

**Pending Implementation:**
- CRUD operations for cosmetic items (models exist, views needed)
- Notification scheduling logic (models exist, scheduling needed)
- Complete LLM API integration with OpenAI
- Frontend login/logout system (Django auth configured)
- Statistics dashboard backend (Chart.js templates ready)
- Advanced item search and filtering

## Coding Standards

- **File Separation**: HTML, CSS, JavaScript must be in separate files
- **No Inline Styles**: All styling through CSS files
- **No Inline Scripts**: All JavaScript in separate files
- **Responsive Design**: Bootstrap mobile-first approach
- **Accessibility**: Proper ARIA labels and semantic HTML

## Deployment Notes

- **Target Platform**: PythonAnywhere
- **External APIs**: OpenAI API for LLM functionality
- **Image Storage**: Local storage initially, cloud storage (S3/Cloudinary) planned
- **Security**: Development secret key present (needs production change)