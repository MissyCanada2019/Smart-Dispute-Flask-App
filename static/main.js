// Enhanced notification functions with error handling (global access)
function markAsRead(notificationId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }
    
    fetch(`/notifications/api/mark-read/${notificationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.remove('unread');
                // Try both old and new Bootstrap class names
                notification.querySelector('.badge-primary')?.remove();
                notification.querySelector('.bg-primary')?.remove();
                notification.querySelector('.notification-actions')?.remove();
            }
            updateNotificationBadge();
        } else {
            console.error('Failed to mark notification as read:', data.error);
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

function markAllAsRead() {
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }
    
    fetch('/notifications/api/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                item.classList.remove('unread');
                // Try both old and new Bootstrap class names
                item.querySelector('.badge-primary')?.remove();
                item.querySelector('.bg-primary')?.remove();
                item.querySelector('.notification-actions')?.remove();
            });
            updateNotificationBadge();
        } else {
            console.error('Failed to mark all notifications as read:', data.error);
        }
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
    });
}

function updateNotificationBadge() {
    fetch('/notifications/api/summary')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const badge = document.querySelector('#notificationDropdown .badge');
        if (data.unread_count > 0) {
            if (badge) {
                badge.textContent = data.unread_count <= 99 ? data.unread_count : '99+';
            } else {
                const button = document.getElementById('notificationDropdown');
                if (button) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'badge bg-danger rounded-pill position-absolute';
                    newBadge.style.cssText = 'top: -5px; right: -5px; font-size: 0.7rem;';
                    newBadge.textContent = data.unread_count <= 99 ? data.unread_count : '99+';
                    button.appendChild(newBadge);
                }
            }
        } else if (badge) {
            badge.remove();
        }
    })
    .catch(error => {
        console.error('Error updating notification badge:', error);
    });
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name=csrf-token]');
    if (meta) {
        return meta.getAttribute('content');
    }
    
    // Fallback: try to get from form
    const input = document.querySelector('input[name=csrf_token]');
    if (input) {
        return input.value;
    }
    
    return '';
}

// Bootstrap 4 to 5 Compatibility Layer (runs after DOM loads)
document.addEventListener('DOMContentLoaded', function() {
    // Fix Bootstrap 4 badge classes to Bootstrap 5
    const badgeClasses = {
        'badge-primary': 'bg-primary',
        'badge-secondary': 'bg-secondary',
        'badge-success': 'bg-success',
        'badge-danger': 'bg-danger',
        'badge-warning': 'bg-warning',
        'badge-info': 'bg-info',
        'badge-light': 'bg-light',
        'badge-dark': 'bg-dark',
        'badge-pill': 'rounded-pill'
    };
    
    // Fix spacing classes
    const spacingClasses = {
        'mr-1': 'me-1', 'mr-2': 'me-2', 'mr-3': 'me-3', 'mr-4': 'me-4', 'mr-5': 'me-5',
        'ml-1': 'ms-1', 'ml-2': 'ms-2', 'ml-3': 'ms-3', 'ml-4': 'ms-4', 'ml-5': 'ms-5',
        'pr-1': 'pe-1', 'pr-2': 'pe-2', 'pr-3': 'pe-3', 'pr-4': 'pe-4', 'pr-5': 'pe-5',
        'pl-1': 'ps-1', 'pl-2': 'ps-2', 'pl-3': 'ps-3', 'pl-4': 'ps-4', 'pl-5': 'ps-5'
    };
    
    // Apply class fixes to all elements
    const allClasses = {...badgeClasses, ...spacingClasses};
    
    for (const [oldClass, newClass] of Object.entries(allClasses)) {
        const elements = document.querySelectorAll('.' + oldClass);
        elements.forEach(element => {
            element.classList.remove(oldClass);
            element.classList.add(newClass);
        });
    }
    
    // Fix data-toggle attributes
    const toggleElements = document.querySelectorAll('[data-toggle]');
    toggleElements.forEach(element => {
        const toggleValue = element.getAttribute('data-toggle');
        element.removeAttribute('data-toggle');
        element.setAttribute('data-bs-toggle', toggleValue);
    });
    
    // Fix dropdown-menu-right to dropdown-menu-end
    const dropdownMenus = document.querySelectorAll('.dropdown-menu-right');
    dropdownMenus.forEach(menu => {
        menu.classList.remove('dropdown-menu-right');
        menu.classList.add('dropdown-menu-end');
    });
    
    console.log('Bootstrap 4 to 5 compatibility fixes applied');
    
    // Auto-refresh notifications every 2 minutes
    setInterval(function() {
        if (typeof updateNotificationBadge === 'function') {
            updateNotificationBadge();
        }
    }, 120000);

    // Global error handler for uncaught JavaScript errors
    window.addEventListener('error', function(event) {
        console.error('JavaScript error caught:', event.error);
        console.error('Error details:', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
        
        // Don't show error to user for now, just log it
        return false;
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        event.preventDefault();
    });
});