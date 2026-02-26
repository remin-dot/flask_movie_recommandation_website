// Auto-dismiss alerts after 5 seconds
(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
})();

// Make movie cards clickable
(function() {
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function(e) {
            // Don't navigate if clicking on interactive elements like buttons
            if (e.target.closest('button, .btn, a:not(.card)')) {
                return;
            }
            const link = this.querySelector('a[href]');
            if (link) {
                window.location.href = link.href;
            }
        });
        // Add hover effect
        card.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 16px rgba(102, 126, 234, 0.2)';
        });
        card.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
})();

// Watchlist Functions
function addToWatchlist(movieId) {
    fetch(`/add-to-watchlist/${movieId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Added to watchlist!', 'success');
            // Reload page or update UI
            location.reload();
        } else {
            showNotification('Error adding to watchlist', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'danger');
    });
}

function removeFromWatchlist(movieId) {
    if (!confirm('Remove from watchlist?')) return;
    
    fetch(`/remove-from-watchlist/${movieId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Removed from watchlist', 'success');
            location.reload();
        } else {
            showNotification('Error removing from watchlist', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'danger');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             role="alert" style="top: 20px; right: 20px; z-index: 9999; max-width: 400px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.body;
    container.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert.position-fixed');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 3000);
}

// Smooth scroll for anchor links
(function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
})();

// Form validation
(function() {
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
})();

// Loading indicator
function showLoading() {
    const loader = document.createElement('div');
    loader.innerHTML = `
        <div class="position-fixed top-50 start-50 translate-middle" style="z-index: 9999;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.querySelector('.spinner-border');
    if (loader) {
        loader.parentElement.remove();
    }
}

// Responsive navigation
(function() {
    const navToggle = document.querySelector('.navbar-toggler');
    const navMenu = document.querySelector('.navbar-collapse');
    
    if (navToggle && navMenu) {
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Don't close on dropdown items
                if (!link.classList.contains('dropdown-toggle')) {
                    navToggle.click();
                }
            });
        });
    }
})();

// Top search autocomplete
(function() {
    const searchInput = document.getElementById('topSearchInput');
    const suggestionsBox = document.getElementById('searchSuggestions');

    if (!searchInput || !suggestionsBox) return;

    let debounceTimer;

    function hideSuggestions() {
        suggestionsBox.classList.remove('show');
        suggestionsBox.innerHTML = '';
        searchInput.setAttribute('aria-expanded', 'false');
    }

    function renderSuggestions(items) {
        if (!items || !items.length) {
            hideSuggestions();
            return;
        }

        suggestionsBox.innerHTML = items.map(item => `
            <button type="button" class="search-suggestion-item" role="option" data-title="${item.title.replace(/"/g, '&quot;')}">
                <span>${item.title}</span>
                <small class="text-muted">${item.year || ''}</small>
            </button>
        `).join('');

        suggestionsBox.classList.add('show');
        searchInput.setAttribute('aria-expanded', 'true');
    }

    async function fetchSuggestions(query) {
        const response = await fetch(`/search/suggest?q=${encodeURIComponent(query)}`);
        if (!response.ok) return [];
        const data = await response.json();
        return data.suggestions || [];
    }

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            hideSuggestions();
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const suggestions = await fetchSuggestions(query);
                renderSuggestions(suggestions);
            } catch (error) {
                console.error('Autocomplete error:', error);
                hideSuggestions();
            }
        }, 220);
    });

    suggestionsBox.addEventListener('click', function(event) {
        const button = event.target.closest('.search-suggestion-item');
        if (!button) return;

        searchInput.value = button.dataset.title || '';
        hideSuggestions();
        const form = searchInput.closest('form');
        if (form) form.submit();
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.search-form-wrapper')) {
            hideSuggestions();
        }
    });

    searchInput.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            hideSuggestions();
        }
    });
})();

// Lazy load images
(function() {
    if ('IntersectionObserver' in window) {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        images.forEach(img => imageObserver.observe(img));
    }
})();

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Export functions for global use
window.addToWatchlist = addToWatchlist;
window.removeFromWatchlist = removeFromWatchlist;
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatNumber = formatNumber;

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
