/**
 * Manufacturing ERP System - Main JavaScript File
 * Handles common functionality across the application
 */

// Global application object
window.ManufacturingERP = {
    // Configuration
    config: {
        autoRefreshInterval: 300000, // 5 minutes
        notificationDuration: 5000,
        chartColors: {
            primary: '#1e40af',
            success: '#059669',
            warning: '#d97706',
            danger: '#dc2626',
            info: '#0284c7',
            secondary: '#64748b'
        }
    },

    // Initialize application
    init: function() {
        this.initBootstrapComponents();
        this.initFormValidations();
        this.initTableEnhancements();
        this.initNotifications();
        this.initAutoRefresh();
        this.initKeyboardShortcuts();
        this.initProgressBars();
        console.log('Manufacturing ERP System initialized successfully');
    },

    // Initialize Bootstrap components
    initBootstrapComponents: function() {
        // Initialize all tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                delay: { show: 500, hide: 100 }
            });
        });

        // Initialize all popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Auto-hide alerts after 5 seconds
        setTimeout(function() {
            var alerts = document.querySelectorAll('.alert-dismissible');
            alerts.forEach(function(alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, this.config.notificationDuration);
    },

    // Enhanced form validations
    initFormValidations: function() {
        // Add real-time validation feedback
        var forms = document.querySelectorAll('form');
        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Focus on first invalid field
                    var firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
                form.classList.add('was-validated');
            });

            // Real-time validation for inputs
            var inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
                input.addEventListener('input', function() {
                    if (input.checkValidity()) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                    } else {
                        input.classList.remove('is-valid');
                        input.classList.add('is-invalid');
                    }
                });
            });
        });

        // Confirm before form submission for delete actions
        var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(event) {
                var message = this.getAttribute('data-confirm-delete') || 'Are you sure you want to delete this item?';
                if (!confirm(message)) {
                    event.preventDefault();
                }
            });
        });
    },

    // Table enhancements
    initTableEnhancements: function() {
        // Add sorting functionality to tables
        var tables = document.querySelectorAll('table[data-sortable]');
        tables.forEach(function(table) {
            ManufacturingERP.makeSortable(table);
        });

        // Add row selection functionality
        var selectableRows = document.querySelectorAll('tr[data-selectable]');
        selectableRows.forEach(function(row) {
            row.addEventListener('click', function() {
                this.classList.toggle('table-active');
                var checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                }
            });
        });

        // Batch actions
        var selectAllCheckbox = document.querySelector('#selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                var checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = selectAllCheckbox.checked;
                    var row = checkbox.closest('tr');
                    if (checkbox.checked) {
                        row.classList.add('table-active');
                    } else {
                        row.classList.remove('table-active');
                    }
                });
            });
        }
    },

    // Make table sortable
    makeSortable: function(table) {
        var headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(function(header, index) {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
            
            header.addEventListener('click', function() {
                ManufacturingERP.sortTable(table, index);
            });
        });
    },

    // Sort table by column
    sortTable: function(table, column) {
        var tbody = table.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var isAscending = !table.getAttribute('data-sort-direction') || table.getAttribute('data-sort-direction') === 'desc';
        
        rows.sort(function(a, b) {
            var aVal = a.cells[column].textContent.trim();
            var bVal = b.cells[column].textContent.trim();
            
            // Try to parse as numbers
            var aNum = parseFloat(aVal.replace(/[^\d.-]/g, ''));
            var bNum = parseFloat(bVal.replace(/[^\d.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // Sort as strings
            return isAscending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        });

        // Clear and re-append sorted rows
        tbody.innerHTML = '';
        rows.forEach(function(row) {
            tbody.appendChild(row);
        });

        // Update sort direction
        table.setAttribute('data-sort-direction', isAscending ? 'asc' : 'desc');
        
        // Update sort icons
        var headers = table.querySelectorAll('th[data-sortable] i');
        headers.forEach(function(icon, index) {
            if (index === column) {
                icon.className = isAscending ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
            } else {
                icon.className = 'fas fa-sort text-muted';
            }
        });
    },

    // Notification system
    initNotifications: function() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            var container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1060; max-width: 350px;';
            document.body.appendChild(container);
        }
    },

    // Show notification
    showNotification: function(message, type = 'info', duration = 5000) {
        var container = document.getElementById('notification-container');
        var notification = document.createElement('div');
        
        var iconMap = {
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle', 
            'danger': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        
        notification.className = `alert alert-${type} alert-dismissible fade show shadow-sm`;
        notification.innerHTML = `
            <i class="${iconMap[type]} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(function() {
            if (notification.parentNode) {
                var bsAlert = new bootstrap.Alert(notification);
                bsAlert.close();
            }
        }, duration);
    },

    // Auto-refresh functionality
    initAutoRefresh: function() {
        // Only auto-refresh on dashboard and list pages
        var autoRefreshPages = ['/dashboard', '/employees', '/machines', '/tools', '/work-orders', '/inspections'];
        var currentPath = window.location.pathname;
        
        if (autoRefreshPages.some(page => currentPath.includes(page))) {
            setInterval(function() {
                // Check if user is active (moved mouse in last 5 minutes)
                if (ManufacturingERP.isUserActive()) {
                    ManufacturingERP.refreshPageData();
                }
            }, this.config.autoRefreshInterval);
        }
    },

    // Check if user is active
    isUserActive: function() {
        // Simple activity detection - in production, this would be more sophisticated
        return document.visibilityState === 'visible';
    },

    // Refresh page data
    refreshPageData: function() {
        // In a real application, this would make AJAX calls to refresh data
        console.log('Auto-refreshing page data...');
        
        // Show refresh indicator
        var indicator = document.createElement('div');
        indicator.className = 'position-fixed top-0 end-0 p-3';
        indicator.innerHTML = '<div class="toast show" role="alert"><div class="toast-body"><i class="fas fa-sync-alt fa-spin me-2"></i>Refreshing data...</div></div>';
        document.body.appendChild(indicator);
        
        setTimeout(function() {
            document.body.removeChild(indicator);
        }, 2000);
    },

    // Keyboard shortcuts
    initKeyboardShortcuts: function() {
        document.addEventListener('keydown', function(event) {
            // Ctrl/Cmd + S to save forms
            if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                event.preventDefault();
                var submitButton = document.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                    ManufacturingERP.showNotification('Form saved via keyboard shortcut', 'success');
                }
            }
            
            // Escape to close modals
            if (event.key === 'Escape') {
                var openModal = document.querySelector('.modal.show');
                if (openModal) {
                    var modalInstance = bootstrap.Modal.getInstance(openModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            }
            
            // Ctrl/Cmd + F to focus search
            if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
                var searchInput = document.querySelector('input[type="search"], input[name="search"], input[placeholder*="search" i]');
                if (searchInput) {
                    event.preventDefault();
                    searchInput.focus();
                    searchInput.select();
                }
            }
        });
    },

    // Initialize progress bars with animations
    initProgressBars: function() {
        var progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(function(bar) {
            var width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            setTimeout(function() {
                bar.style.transition = 'width 1s ease-in-out';
                bar.style.width = width;
            }, 100);
        });
    },

    // Utility functions
    utils: {
        // Format currency
        formatCurrency: function(amount) {
            if (amount === null || amount === undefined) return '₹0.00';
            return new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR'
            }).format(amount);
        },

        // Format date
        formatDate: function(date, format = 'dd-MM-yyyy') {
            if (!date) return '-';
            if (typeof date === 'string') date = new Date(date);
            
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            
            switch (format) {
                case 'dd-MM-yyyy':
                    return `${day}-${month}-${year}`;
                case 'MM/dd/yyyy':
                    return `${month}/${day}/${year}`;
                case 'yyyy-MM-dd':
                    return `${year}-${month}-${day}`;
                default:
                    return date.toLocaleDateString();
            }
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Generate unique ID
        generateId: function() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        },

        // Validate email
        isValidEmail: function(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        // Copy to clipboard
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(function() {
                    ManufacturingERP.showNotification('Copied to clipboard', 'success', 2000);
                });
            } else {
                // Fallback for older browsers
                var textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                ManufacturingERP.showNotification('Copied to clipboard', 'success', 2000);
            }
        }
    },

    // Chart utilities for reports
    charts: {
        // Default chart options
        defaultOptions: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        },

        // Create line chart
        createLineChart: function(ctx, data, options = {}) {
            return new Chart(ctx, {
                type: 'line',
                data: data,
                options: { ...this.defaultOptions, ...options }
            });
        },

        // Create bar chart
        createBarChart: function(ctx, data, options = {}) {
            return new Chart(ctx, {
                type: 'bar',
                data: data,
                options: { ...this.defaultOptions, ...options }
            });
        },

        // Create pie chart
        createPieChart: function(ctx, data, options = {}) {
            return new Chart(ctx, {
                type: 'pie',
                data: data,
                options: { ...this.defaultOptions, ...options }
            });
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    ManufacturingERP.init();
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    ManufacturingERP.showNotification('An error occurred. Please try again.', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    ManufacturingERP.showNotification('An error occurred. Please try again.', 'danger');
});

// Service Worker registration (for future PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker would be registered here in production
        console.log('Service Worker support detected');
    });
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ManufacturingERP;
}
