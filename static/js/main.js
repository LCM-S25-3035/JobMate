/**
 * JobMate Main JavaScript File
 * Handles authentication, form validation, and UI interactions
 */

// Global JobMate namespace
window.JobMate = {
    init: function() {
        this.initTooltips();
        this.initAnimations();
        this.initFormValidation();
        this.initSearchFunctionality();
        this.initThemeToggle();
    },

    // Initialize Bootstrap tooltips
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialize animations
    initAnimations: function() {
        // Fade in animations for cards
        const cards = document.querySelectorAll('.card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        cards.forEach(card => {
            observer.observe(card);
        });

        // Stagger animations for dashboard cards
        const dashboardCards = document.querySelectorAll('.dashboard-card');
        dashboardCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    },

    // Form validation utilities
    initFormValidation: function() {
        // Real-time validation for all forms
        const forms = document.querySelectorAll('form[novalidate]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                input.addEventListener('input', () => {
                    if (input.classList.contains('is-invalid')) {
                        this.validateField(input);
                    }
                });
            });
        });
    },

    validateField: function(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let message = '';

        // Required field validation
        if (required && !value) {
            isValid = false;
            message = 'This field is required';
        }
        
        // Email validation
        else if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
        }
        
        // Password validation
        else if (type === 'password' && value) {
            if (value.length < 8) {
                isValid = false;
                message = 'Password must be at least 8 characters';
            }
        }
        
        // Phone validation
        else if (field.name === 'phone' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
                isValid = false;
                message = 'Please enter a valid phone number';
            }
        }

        this.setFieldValidation(field, isValid, message);
        return isValid;
    },

    setFieldValidation: function(field, isValid, message) {
        const feedback = field.parentNode.querySelector('.invalid-feedback') || 
                        field.nextElementSibling;
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedback) feedback.textContent = '';
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = message;
        }
    },

    // Search functionality
    initSearchFunctionality: function() {
        const searchInput = document.getElementById('globalSearch');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    this.performSearch(query);
                }, 300);
            }
        });
    },

    performSearch: function(query) {
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data.results);
            })
            .catch(error => console.error('Search error:', error));
    },

    displaySearchResults: function(results) {
        // Implementation for search results dropdown
        console.log('Search results:', results);
    },

    // Theme toggle
    initThemeToggle: function() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;

        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    },

    // Utility functions
    showAlert: function(type, message, container = null) {
        const alertId = 'alert-' + Date.now();
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="bi bi-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const targetContainer = container || document.querySelector('.container');
        if (targetContainer) {
            targetContainer.insertAdjacentHTML('afterbegin', alertHtml);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    alert.classList.remove('show');
                    setTimeout(() => alert.remove(), 150);
                }
            }, 5000);
        }
    },

    getAlertIcon: function(type) {
        const icons = {
            'success': 'check-circle-fill',
            'danger': 'exclamation-triangle-fill',
            'warning': 'exclamation-triangle-fill',
            'info': 'info-circle-fill'
        };
        return icons[type] || 'info-circle-fill';
    },

    // Form submission with loading state
    submitForm: function(form, endpoint, options = {}) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2"></span>
            ${options.loadingText || 'Processing...'}
        `;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        return fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': form.querySelector('[name=csrf_token]').value
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showAlert('success', data.message || 'Operation completed successfully');
                if (options.onSuccess) options.onSuccess(data);
            } else {
                this.showAlert('danger', data.message || 'An error occurred');
                if (options.onError) options.onError(data);
            }
            return data;
        })
        .catch(error => {
            console.error('Form submission error:', error);
            this.showAlert('danger', 'An unexpected error occurred');
            if (options.onError) options.onError(error);
        })
        .finally(() => {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    },

    // Copy to clipboard utility
    copyToClipboard: function(text, successMessage = 'Copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            this.showAlert('success', successMessage);
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showAlert('success', successMessage);
        });
    },

    // Format currency
    formatCurrency: function(amount, currency = 'CAD') {
        return new Intl.NumberFormat('en-CA', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format date
    formatDate: function(dateString) {
        return new Intl.DateTimeFormat('en-CA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(dateString));
    }
};

// Authentication specific functions
window.JobMate.Auth = {
    // Login form handler
    handleLogin: function(form) {
        return JobMate.submitForm(form, '/auth/api/login', {
            loadingText: 'Signing in...',
            onSuccess: function(data) {
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/dashboard';
                }, 1000);
            }
        });
    },

    // Registration form handler
    handleRegistration: function(form) {
        return JobMate.submitForm(form, '/auth/api/register', {
            loadingText: 'Creating account...',
            onSuccess: function(data) {
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
            }
        });
    },

    // Email availability check
    checkEmailAvailability: function(email) {
        return fetch(`/auth/check-email?email=${encodeURIComponent(email)}`)
            .then(response => response.json());
    },

    // Password strength calculator
    calculatePasswordStrength: function(password) {
        let score = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            symbols: /[^A-Za-z0-9]/.test(password)
        };

        Object.values(checks).forEach(check => {
            if (check) score++;
        });

        const strength = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][score];
        const percentage = (score / 5) * 100;

        return { score, strength, percentage, checks };
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    JobMate.init();
    
    // Add any page-specific initializations
    if (document.body.classList.contains('auth-page')) {
        // Auth page specific code
        console.log('Auth page loaded');
    }
    
    if (document.body.classList.contains('dashboard-page')) {
        // Dashboard specific code
        console.log('Dashboard page loaded');
    }
});

// Export for use in other modules
window.JobMate = JobMate; 