# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このプロジェクトは、化粧品やメイク用品の **使用期限を管理するアプリ** です。  
ユーザーは商品名・開封日・カテゴリ・形状などを登録することで、自動的に使用期限を計算・通知を受け取れます。  
また、LLM（ChatGPT API）を利用してカテゴリや形状を自動補完し、衛生リスクや使用ペース改善のアドバイスを提示します。  
ポートフォリオとして、実務で使える設計力・実装力・デザイン力をアピールする目的も含みます。

## Common Development Commands

### Django Management Commands

```bash
# Start development server
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate

# Admin operations
python manage.py createsuperuser

# Testing and maintenance
python manage.py check
python manage.py test
python manage.py shell

# Static files (if needed)
python manage.py collectstatic
```

### Database Management

```bash
# View migration status
python manage.py showmigrations

# Create specific app migrations
python manage.py makemigrations beauty

# Apply specific migration
python manage.py migrate beauty
```

## Project Architecture

### Django Structure

This is a single-app Django project with the following structure:

- **Main Project**: `cosme_expiry_app/` - Contains settings, main URLs, and WSGI/ASGI configuration
- **Beauty App**: `beauty/` - Main application containing all business logic
  - Models: Currently minimal structure in `models.py`
  - Views: Basic home view in `views.py`
  - Templates: Bootstrap-based responsive design with `base.html` and `home.html`
  - Static files: Separated CSS (`styles.css`, `custom-styles.css`) and JavaScript (`scripts.js`)

### Key Settings

- **Language**: Japanese (`ja`) with Asia/Tokyo timezone
- **Database**: SQLite for development
- **Debug Mode**: Enabled for development
- **Static Files**: Configured with `beauty/static/` directory
- **Templates**: Located in `beauty/templates/`

### Planned Features (Not Yet Implemented)

Based on the templates and existing documentation:

1. **Item Management**: CRUD operations for cosmetic items
2. **Notification System**: Automated expiry notifications (30/14/7 days before, weekly after expiry)
3. **LLM Integration**: ChatGPT API for category/shape auto-completion and advice
4. **User Authentication**: Django's built-in auth system
5. **Statistics Dashboard**: Charts showing category distribution and expiry status
6. **Search and Filtering**: Advanced item filtering capabilities

## File Organization Standards

### Template Structure

- `base.html`: Main template with responsive navbar, mobile menu, and footer
- Uses Bootstrap 5.2.3 with Font Awesome icons
- Chart.js integration for statistics display
- Custom CSS separated into multiple files

### Static Files Organization

```
beauty/static/
├── css/
│   ├── styles.css          # Main styles
│   └── custom-styles.css   # Custom overrides
├── images/
│   ├── favicon.ico
│   └── header.jpg
└── js/
    └── scripts.js          # Main JavaScript
```

### Code Standards

- **File Separation**: HTML, CSS, and JavaScript must be in separate files
- **No Inline Styles**: All styling must be in CSS files
- **No Inline Scripts**: All JavaScript must be in separate JS files
- **Responsive Design**: Mobile-first approach with Bootstrap
- **Accessibility**: Proper ARIA labels and semantic HTML

## Design System

### Color Palette

- Primary: `#f8dec6` (Light cream)
- Secondary: `#c7b19c` (Warm brown)
- Accent: `#d3859c` (Dusty rose)
- Text: `#000000` (Black)

### Design Direction

- Modern and sophisticated urban style
- Clean, minimal interface
- Focus on usability and accessibility

## Development Environment

- **Python**: 3.13.5
- **Django**: 5.2+ (inferred from settings structure)
- **Frontend**: Bootstrap 5.2.3, Font Awesome 6.0.0, Chart.js
- **Database**: SQLite (development)

## Deployment Configuration

- **Target Platform**: PythonAnywhere
- **External APIs**: OpenAI API for LLM features
- **Image Storage**: Local storage initially, cloud storage (S3/Cloudinary) planned
- **Security**: Development secret key present (change for production)

## Development Notes

- Models are currently minimal and need implementation based on planned features
- Authentication system not yet implemented
- LLM integration not yet implemented  
- Charts and statistics features are templated but need backend implementation
- Mobile responsiveness is fully implemented in templates