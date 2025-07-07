# Template Context Management - QuantumVestAI

## Overview

This document explains the template context management system implemented to fix critical template errors and ensure robust template rendering.

## Critical Issues Fixed

### 1. 'now' Variable Undefined Error
**Problem**: Templates were using `{{ now.year }}` and `{{ now.strftime() }}` but the `now` variable was not defined in the template context.

**Solution**: Added global template variables in `main.py`:
```python
templates.env.globals["now"] = datetime.utcnow
templates.env.globals["current_year"] = datetime.utcnow().year
templates.env.globals["app_name"] = "QuantumVestAI"
```

### 2. Missing Template Filters
**Problem**: Templates were using filters like `format_change_value` that weren't registered.

**Solution**: Verified and confirmed proper registration of all template filters in `ui/utils/template_filters.py`.

## Template Usage Patterns

### Safe Date/Time Access
```jinja2
<!-- Recommended: Safe access with fallback -->
{% if now is defined %}{{ now().year }}{% else %}{{ current_year|default('2025') }}{% endif %}

<!-- Also works: Direct access (now available globally) -->
{{ now().year }}
{{ now().strftime('%Y-%m-%d') }}
{{ now().strftime('%B %d, %Y') }}
```

### Filter Usage
```jinja2
<!-- Change value formatting -->
{{ value|format_change_value }}  <!-- +1.23 or -0.56 -->

<!-- Large number formatting -->
{{ value|format_large_number }}  <!-- 1.5M, 2.3K, etc. -->

<!-- Currency formatting -->
{{ value|format_currency }}      <!-- $1,234.56 -->

<!-- Percentage formatting -->
{{ value|format_percentage }}    <!-- 525.00% -->
```

## Available Template Globals

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `now` | function | Returns current UTC datetime | `{{ now().year }}` |
| `current_year` | int | Current year | `{{ current_year }}` |
| `app_name` | string | Application name | `{{ app_name }}` |
| `app_version` | string | Application version | `{{ app_version }}` |
| `API_URL` | string | API base URL | `{{ API_URL }}` |

## Template Context Processor

The `TemplateContextProcessor` class in `ui/utils/template_context.py` provides:

- **Base Context**: Common variables for all templates
- **User Context**: User-specific variables when authenticated
- **Request Context**: Request-specific variables
- **Safe Fallbacks**: Graceful error handling

### Usage Example
```python
from ui.utils.template_context import TemplateContextProcessor

processor = TemplateContextProcessor()
context = processor.create_template_context(request, user_data=user)
return templates.TemplateResponse("template.html", context)
```

## Template Safety Best Practices

### 1. Safe Variable Access
```jinja2
<!-- Check if variable is defined -->
{% if variable is defined %}
    {{ variable.method() }}
{% else %}
    Fallback content
{% endif %}
```

### 2. Default Values
```jinja2
<!-- Use default filter for missing values -->
{{ variable|default('Default Value') }}
{{ user.name|default('Guest') }}
```

### 3. Error Boundaries
```jinja2
<!-- Wrap risky operations -->
{% try %}
    {{ complex_operation() }}
{% except %}
    <p>Content unavailable</p>
{% endtry %}
```

## Files Modified

### Core Application
- `main.py`: Added template global variables setup
- `ui/utils/template_context.py`: New comprehensive context processor

### Templates Updated
- `ui/templates/base.html`: Safe copyright year access
- `ui/templates/home.html`: Safe market date display  
- `ui/templates/auth/*.html`: Already had safe patterns (verified)

## Testing

Run the test suite to verify fixes:
```bash
python test_template_fixes.py
```

Run the demonstration to see before/after:
```bash
python demonstrate_fixes.py
```

## Error Handling

The system now provides:

1. **Graceful Fallbacks**: Templates render even with missing variables
2. **Error Logging**: Comprehensive logging for debugging
3. **Safe Defaults**: Sensible default values for missing context
4. **Validation**: Template filter and context validation

## Monitoring

Template errors are logged with details:
- Error type and message
- Template name and location
- Request context
- Fallback actions taken

Check application logs for template-related issues:
```bash
tail -f logs/app.log | grep -i template
```