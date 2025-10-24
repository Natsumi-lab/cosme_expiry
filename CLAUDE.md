# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cosmetic expiry tracking application built with Django. Users can register cosmetic products with their opening dates and automatically receive expiry calculations and notifications. The app integrates LLM (ChatGPT API) to auto-suggest categories and provide hygiene risk assessments and usage improvement advice.

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

# Create test data
python manage.py shell
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

## Architecture Overview

### Core Models (`beauty/models.py`)

1. **BaseModel** (lines 5-11): Abstract base with timestamps
   - Provides `created_at` and `updated_at` fields to all models
   - Inherited by all main models for consistent auditing

2. **Taxon** (lines 14-49): Hierarchical category system
   - Self-referencing tree structure for cosmetic categories
   - Auto-calculates `depth` and `full_path` on save via custom save method
   - `is_leaf` property determines if category can be assigned to items
   - Used for organizing products (e.g., Makeup > Lips > Lip Gloss)

3. **Item** (lines 52-127): Main product entity
   - User ownership enforced via ForeignKey with CASCADE deletion
   - Uses Taxon for hierarchical categorization via `product_type` field
   - Tracks opening date, expiry date, and status ('using'/'finished')
   - Risk assessment levels ('low'/'mid'/'high') for expiry alerts
   - Image support via both URL and file upload fields
   - Properties: `main_category`, `middle_category` for navigation breadcrumbs

4. **Notification** (lines 130-153): Automated alert system
   - Types: 30-day, 14-day, 7-day warnings, and overdue alerts
   - Links to User and Item with CASCADE deletion
   - Scheduled notification system with read status tracking
   - Notification badge UI with counters for different timeframes

5. **LlmSuggestionLog** (lines 156-199): AI integration tracking
   - Records LLM suggestions vs user choices for learning
   - Links both suggested and chosen taxons for analysis
   - Tracks suggestion acceptance rate by target type (category/product_name/brand)

### Authentication System

Email-based authentication instead of username:
- `SignUpForm` (`beauty/forms.py:9-96`): Custom registration with email validation and password strength checks
- `SignInView` (`beauty/views.py:74-133`): Email lookup for login authentication
- All item operations require login and enforce user ownership for security

### Admin Interface (`beauty/admin.py`)

- Taxon admin restricts Item.product_type to leaf nodes only (line 28)
- Advanced filtering by category hierarchy levels
- Date hierarchy for notifications and items

### Frontend Architecture

**Template System**:
- `base.html`: Responsive Bootstrap layout with Chart.js integration
- Navigation with offcanvas mobile menu
- Statistics dashboard with sample data (`beauty/static/js/scripts.js`)

**Item List Implementation**:
- Multi-tab interface for expiry status filtering (expired, 7 days, 14 days, etc.)
- Advanced hierarchical category filtering with dynamic selects
- Custom JavaScript handling in `item-list.js` for AJAX loading of category options
- Responsive card layout for displaying items with risk indicators

**Notification System**:
- Dropdown accordion interface for notification categories
- Grid-based layout for notification headers with responsive spacing
- Badge counters for each expiry timeframe (7-day, 14-day, 30-day, expired)
- Real-time notification status updates via JavaScript

**Design System**:
- Primary: `#f8dec6` (Light Cream)
- Accent: `#d3859c` (Dusty Rose)
- Bootstrap 5.2.3 with responsive breakpoints
- Risk status color coding: green (safe), yellow (7-day), orange (14-day), red (expired)

## Configuration Details

### Settings (`cosme_expiry_app/settings.py`)

- **Language**: Japanese (`ja`) with Asia/Tokyo timezone
- **Database**: SQLite for development (UTC storage with timezone-aware display)
- **Static Files**: Served from `beauty/static/`
- **Templates**: Located in `beauty/templates/`
- **Media Files**: User uploads stored in `media/` directory
- **Virtual Environment**: Uses `venv/` directory
- **Authentication**: Custom email-based login system
- **Environment Variables**: Uses python-dotenv for configuration (OPENAI_API_KEY)

### URL Configuration (`beauty/urls.py`)

```
/                         # Home (login required)
/signup/                  # User registration  
/signin/                  # User login
/signout/                 # User logout
/items/                   # Item list view
/items/new/               # Create new item
/items/<id>/              # Item detail view
/items/<id>/edit/         # Edit item
/api/taxons/              # Taxon hierarchy API
/api/notifications/       # Notification API endpoints
/admin/                   # Django admin interface
```

## View Implementation Patterns

### Security Pattern
All item views follow this pattern (`beauty/views.py:372-379`, `beauty/views.py:435-442`):
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

### Form Validation
- Cross-field validation in `ItemForm.clean()` (`beauty/forms.py:236-245`)
- Email uniqueness check in `SignUpForm.clean_email()` (`beauty/forms.py:67-72`)
- Password strength validation (`beauty/forms.py:74-87`)

### Item List View Implementation
The item list view (`beauty/views.py:241-365`) includes:
- Comprehensive filtering by expiry status (expired, week, biweek, month, safe)
- Search functionality across item names
- Category filtering with hierarchical support
- Status filtering (using/finished)
- Multiple sort options
- Risk level calculation with color-coded display
- Tab counting for UI badges

### JavaScript Integration
The application uses modern JavaScript for dynamic features:
- `item-list.js`: Handles hierarchical filtering and AJAX category loading
- `item-form.js`: Manages dynamic form behavior and validation
- `scripts.js`: Core site functionality and Chart.js dashboard
- `notifications.js`: Manages notification loading, badge updates, and read/unread status

## Notification System

### Notification Management Command
Custom command (`beauty/management/commands/generate_notifications.py`) for generating time-based notifications:
- Automated daily check for expiring items
- Transaction-based atomic creation of notifications
- Multiple notification types based on time remaining:
  - `OVERWEEK`: Weekly reminders for expired items (Monday only)
  - `D7`: 7-day expiry warnings
  - `D14`: 14-day expiry warnings
  - `D30`: 30-day expiry warnings
- Database-driven scheduling with duplicate prevention

### Notification APIs
- `/api/notifications/summary/`: Returns counts of unread notifications by type
- `/api/notifications/mark-read/`: Marks notifications as read based on type

### Notification UI
- Dropdown menu with styled notification headers
- Badge counters for each notification category
- Responsive grid layout with optimized spacing between text and badge
- Animation effects for unread notification badges

## LLM Integration Framework

**Framework Functions** (`beauty/views.py:163-201`):
- `process_llm_suggestion()`: Framework for LLM API calls with Taxon suggestions
- `confirm_llm_suggestion()`: User confirmation handling and learning log

**Management Commands**:
- `generate_notifications.py`: Custom command for scheduled notification generation

## Development Environment

- **Python**: 3.13+
- **Django**: 5.2.4
- **Frontend**: Bootstrap 5.2.3, Font Awesome 6.0.0, Chart.js
- **Database**: SQLite (development)
- **Image Processing**: Pillow>=11.3.0
- **Environment Variables**: python-dotenv for API keys and configuration

### Testing

No testing framework currently configured. Standard Django tests available:
- Use `python manage.py test` for running tests
- Use `python manage.py test beauty` for app-specific tests
- No lint/format tools currently configured (black, flake8 planned in requirements.txt)

## Implementation Status

**Completed:**
- Complete data model structure with migrations applied
- User authentication system with email-based login
- Admin interface with hierarchical category restrictions
- Item CRUD operations (create, list, detail, edit views)
- Frontend templates with responsive design
- LLM integration framework structure
- API endpoint for hierarchical taxon data
- Item listing with filtering and sorting
- Notification UI implementation with badge counts
- Notification generation command structure
- Notification styling and layout improvements

**In Progress:**
- Notification scheduling automation
- API integration with frontend for real-time notification updates

**Pending Implementation:**
- Complete LLM API integration with OpenAI
- Statistics dashboard backend (Chart.js ready with sample data)
- Image processing completion

## Coding Standards

- **File Separation**: HTML, CSS, JavaScript in separate files (no inline styles/scripts)
- **Security**: User ownership validation on all item operations
- **Internationalization**: Japanese language with Asia/Tokyo timezone
- **Responsive Design**: Bootstrap mobile-first approach
- **Error Handling**: Comprehensive exception handling in views
- **Grid Layout**: Modern CSS grid used for notification headers and responsive elements