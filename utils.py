from flask_login import current_user
from datetime import datetime
import string
import random


def generate_code(prefix, length=8):
    """Generate a unique code with given prefix"""
    timestamp = datetime.now().strftime('%y%m%d')
    random_part = ''.join(random.choices(string.digits, k=length-len(timestamp)))
    return f"{prefix}{timestamp}{random_part}"


def check_permission(allowed_roles):
    """Check if current user has permission based on role"""
    if not current_user.is_authenticated:
        return False
    return current_user.role in allowed_roles


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "₹0.00"
    return f"₹{amount:,.2f}"


def get_status_badge_class(status):
    """Get Bootstrap badge class for status"""
    status_classes = {
        'Draft': 'bg-secondary',
        'Pending': 'bg-warning',
        'In Progress': 'bg-primary',
        'Completed': 'bg-success',
        'Approved': 'bg-success',
        'Rejected': 'bg-danger',
        'Failed': 'bg-danger',
        'Passed': 'bg-success',
        'Active': 'bg-success',
        'Inactive': 'bg-secondary',
        'Cancelled': 'bg-danger',
        'On Hold': 'bg-warning',
        'Sent': 'bg-info',
        'Delivered': 'bg-success',
        'Closed': 'bg-dark'
    }
    return status_classes.get(status, 'bg-secondary')


def get_priority_badge_class(priority):
    """Get Bootstrap badge class for priority"""
    priority_classes = {
        'Low': 'bg-secondary',
        'Normal': 'bg-primary',
        'High': 'bg-warning',
        'Urgent': 'bg-danger'
    }
    return priority_classes.get(priority, 'bg-secondary')
