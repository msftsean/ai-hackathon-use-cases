// Virtual Citizen Agent - JavaScript Functions
// ================================================

// Global configuration for easy city customization
const VirtualCitizenAgent = {
    config: {
        apiBaseUrl: '/api',
        searchDelay: 300,
        maxResults: 10,
        city: {
            name: 'New York City',
            shortName: 'NYC'
        }
    },
    
    // Search functionality
    search: {
        // Debounced search function
        debounceTimer: null,
        
        // Perform search with debouncing
        performSearch: function(query, callback, delay = VirtualCitizenAgent.config.searchDelay) {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.executeSearch(query, callback);
            }, delay);
        },
        
        // Execute the actual search
        executeSearch: function(query, callback) {
            if (!query || query.trim().length < 2) {
                callback({ error: 'Query too short' });
                return;
            }
            
            const url = `${VirtualCitizenAgent.config.apiBaseUrl}/search/documents?query=${encodeURIComponent(query)}&maxResults=${VirtualCitizenAgent.config.maxResults}`;
            
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => callback(data))
                .catch(error => {
                    console.error('Search error:', error);
                    callback({ error: error.message });
                });
        },
        
        // Semantic search
        performSemanticSearch: function(query, callback) {
            const url = `${VirtualCitizenAgent.config.apiBaseUrl}/search/semantic?query=${encodeURIComponent(query)}&maxResults=${VirtualCitizenAgent.config.maxResults}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => callback(data))
                .catch(error => {
                    console.error('Semantic search error:', error);
                    callback({ error: error.message });
                });
        },
        
        // Search by category
        searchByCategory: function(category, query = '', callback) {
            const url = `${VirtualCitizenAgent.config.apiBaseUrl}/search/categories/${encodeURIComponent(category)}?query=${encodeURIComponent(query)}&maxResults=${VirtualCitizenAgent.config.maxResults}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => callback(data))
                .catch(error => {
                    console.error('Category search error:', error);
                    callback({ error: error.message });
                });
        }
    },
    
    // Category management
    categories: {
        // Get all available categories
        getAll: function(callback) {
            const url = `${VirtualCitizenAgent.config.apiBaseUrl}/search/categories`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => callback(data))
                .catch(error => {
                    console.error('Categories error:', error);
                    callback({ error: error.message });
                });
        }
    },
    
    // UI utilities
    ui: {
        // Show loading state
        showLoading: function(elementId, message = 'Loading...') {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">${message}</span>
                        </div>
                        <p class="mt-2">${message}</p>
                    </div>
                `;
            }
        },
        
        // Show error state
        showError: function(elementId, message = 'Something went wrong') {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                        <h5>Error</h5>
                        <p class="text-muted">${message}</p>
                        <button class="btn btn-outline-primary" onclick="location.reload()">
                            <i class="fas fa-refresh me-2"></i>Try Again
                        </button>
                    </div>
                `;
            }
        },
        
        // Format search results for display
        formatSearchResults: function(data, query = '') {
            if (!data.documents || data.documents.length === 0) {
                return `
                    <div class="text-center py-4">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h5>No results found</h5>
                        <p class="text-muted">Try rephrasing your search or browse our categories.</p>
                        <button class="btn btn-outline-primary" onclick="VirtualCitizenAgent.ui.showCategories()">
                            <i class="fas fa-th-large me-2"></i>Browse Categories
                        </button>
                    </div>
                `;
            }
            
            let html = `
                <div class="search-results-header mb-3">
                    <p class="text-muted mb-2">Found ${data.total_results} results${query ? ` for "${query}"` : ''}</p>
                </div>
            `;
            
            data.documents.forEach((doc, index) => {
                const relevanceScore = doc.relevance_score ? (doc.relevance_score * 100).toFixed(0) : 'N/A';
                const semanticScore = doc.semantic_score ? (doc.semantic_score * 100).toFixed(0) : null;
                
                html += `
                    <div class="search-result-item mb-4 p-3 border rounded">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-1 text-primary">${this.escapeHtml(doc.title)}</h6>
                            <div>
                                <span class="badge bg-secondary me-1">${this.escapeHtml(doc.category)}</span>
                                ${semanticScore ? `<span class="badge bg-info">Semantic: ${semanticScore}%</span>` : ''}
                            </div>
                        </div>
                        <p class="mb-2 text-muted">${this.escapeHtml(doc.content.substring(0, 250))}${doc.content.length > 250 ? '...' : ''}</p>
                        
                        ${doc.highlights && doc.highlights.length > 0 ? `
                            <div class="highlights mb-2">
                                <small class="text-info"><strong>Highlights:</strong></small>
                                <div class="small text-muted">${doc.highlights.map(h => this.escapeHtml(h)).join(' ... ')}</div>
                            </div>
                        ` : ''}
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-tag me-1"></i>${this.escapeHtml(doc.service_type)} • 
                                <i class="fas fa-clock me-1"></i>Updated ${this.formatDate(doc.last_updated)}
                            </small>
                            <span class="badge bg-success">Relevance: ${relevanceScore}%</span>
                        </div>
                        
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="VirtualCitizenAgent.ui.viewDocument('${doc.id}')">
                                <i class="fas fa-eye me-1"></i>View Details
                            </button>
                        </div>
                    </div>
                `;
                
                if (index < data.documents.length - 1) {
                    html += '<hr>';
                }
            });
            
            return html;
        },
        
        // View document details
        viewDocument: function(documentId) {
            console.log('Viewing document:', documentId);
            // Implementation for viewing document details
            // This could open a modal or navigate to a detail page
        },
        
        // Show categories
        showCategories: function() {
            window.location.href = '/Home/Categories';
        },
        
        // Utility functions
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
        
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
    },
    
    // Analytics and tracking
    analytics: {
        trackSearch: function(query, results_count) {
            // Implementation for search analytics
            console.log('Search tracked:', { query, results_count });
        },
        
        trackCategoryView: function(category) {
            // Implementation for category analytics
            console.log('Category viewed:', category);
        }
    },
    
    // Accessibility helpers
    accessibility: {
        announceToScreenReader: function(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'visually-hidden';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        }
    }
};

// Global functions for backward compatibility and ease of use
function performQuickSearch() {
    const query = document.getElementById('headerSearch').value;
    if (query.trim()) {
        window.location.href = '/Home/Search?q=' + encodeURIComponent(query);
    }
}

function performMainSearch() {
    const query = document.getElementById('mainSearchInput').value;
    if (query.trim()) {
        searchQuery(query);
    }
}

function searchQuery(query) {
    const searchInput = document.getElementById('mainSearchInput');
    if (searchInput) {
        searchInput.value = query;
    }
    
    const resultsDiv = document.getElementById('searchResults');
    const contentDiv = document.getElementById('searchResultsContent');
    
    if (resultsDiv && contentDiv) {
        VirtualCitizenAgent.ui.showLoading('searchResultsContent', 'Searching city services...');
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
        
        VirtualCitizenAgent.search.performSearch(query, (data) => {
            if (data.error) {
                VirtualCitizenAgent.ui.showError('searchResultsContent', data.error);
            } else {
                contentDiv.innerHTML = VirtualCitizenAgent.ui.formatSearchResults(data, query);
                VirtualCitizenAgent.analytics.trackSearch(query, data.total_results || 0);
                VirtualCitizenAgent.accessibility.announceToScreenReader(`Found ${data.total_results || 0} results for ${query}`);
            }
        });
    }
}

function searchCategory(category) {
    window.location.href = '/Home/Categories?category=' + encodeURIComponent(category);
    VirtualCitizenAgent.analytics.trackCategoryView(category);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log(`${VirtualCitizenAgent.config.city.name} Virtual Citizen Agent initialized`);
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // ESC key to close search results
        if (e.key === 'Escape') {
            const resultsDiv = document.getElementById('searchResults');
            if (resultsDiv && resultsDiv.style.display !== 'none') {
                resultsDiv.style.display = 'none';
            }
        }
    });
    
    // Initialize search input handlers
    const headerSearch = document.getElementById('headerSearch');
    const mainSearch = document.getElementById('mainSearchInput');
    
    if (headerSearch) {
        headerSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performQuickSearch();
            }
        });
    }
    
    if (mainSearch) {
        mainSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performMainSearch();
            }
        });
        
        // Add autocomplete/suggestions functionality
        mainSearch.addEventListener('input', function(e) {
            const query = e.target.value;
            if (query.length >= 3) {
                // Could implement autocomplete here
                console.log('Could show suggestions for:', query);
            }
        });
    }
});

// Export for use in other scripts
window.VirtualCitizenAgent = VirtualCitizenAgent;