/**
 * FlickBase - Main JavaScript File
 * Handles interactive features and client-side functionality
 */

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Close alert after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Toggle favorite status (for future use)
 */
function toggleFavorite(movieId) {
    const icon = document.getElementById(`favorite-${movieId}`);
    if (icon) {
        icon.classList.toggle('fas');
        icon.classList.toggle('far');
    }
}

/**
 * Show loading spinner
 */
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');
    const span = document.createElement('span');
    span.className = 'visually-hidden';
    span.textContent = 'Loading...';
    spinner.appendChild(span);
    return spinner;
}

/**
 * Handle form submission with loading state
 */
function handleFormSubmit(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 3000);
    }
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Handle real-time search suggestions (for future implementation)
 */
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    const handleSearch = debounce(function(e) {
        const query = e.target.value;
        if (query.length >= 2) {
            // Implement search suggestions here
            console.log('Searching for:', query);
        }
    }, 300);

    searchInput.addEventListener('input', handleSearch);
}

/**
 * Confirm delete actions
 */
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Toggle dark mode (for future implementation)
 */
function toggleDarkMode() {
    const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    if (isDarkMode) {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('theme', 'light');
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

/**
 * Restore user's theme preference
 */
function restoreThemePreference() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
}

// Restore theme preference on page load
window.addEventListener('DOMContentLoaded', restoreThemePreference);

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Highlight text in search results
 */
function highlightSearchText(element, searchText) {
    if (!searchText) return;
    
    const regex = new RegExp(`(${searchText})`, 'gi');
    const htmlContent = element.innerHTML;
    element.innerHTML = htmlContent.replace(regex, '<mark>$1</mark>');
}

/**
 * Rate movie with stars
 */
function rateMovieWithStars(movieId, rating) {
    // Send rating to backend
    console.log(`Rating movie ${movieId} with ${rating} stars`);
}

/**
 * Get average rating
 */
function getAverageRating(ratings) {
    if (ratings.length === 0) return 0;
    const sum = ratings.reduce((acc, rating) => acc + rating, 0);
    return (sum / ratings.length).toFixed(2);
}

/**
 * Validate form inputs
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Handle errors gracefully
 */
function handleError(error, userMessage = 'An error occurred. Please try again.') {
    console.error('Error:', error);
    showToast(userMessage, 'danger');
}
