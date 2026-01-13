/**
 * Emergency Response Agent - Dashboard JavaScript
 * Accessible keyboard navigation and API integration
 */

const API_BASE = '/api/v1';

// DOM Elements
const scenarioForm = document.getElementById('scenario-form');
const loadingEl = document.getElementById('loading');
const planResultsEl = document.getElementById('plan-results');
const apiStatusEl = document.getElementById('api-status');

// Navigation
const navLinks = document.querySelectorAll('nav a');
const sections = {
    'scenario-section': document.getElementById('scenario-section'),
    'weather-section': document.getElementById('weather-section'),
    'evacuation-section': document.getElementById('evacuation-section'),
    'historical-section': document.getElementById('historical-section')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
    setupNavigation();
    setupForm();
    setupKeyboardShortcuts();
});

// Check API Health
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            apiStatusEl.textContent = 'Online';
            apiStatusEl.className = 'online';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        apiStatusEl.textContent = 'Offline';
        apiStatusEl.className = 'offline';
    }
}

// Navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            showSection(targetId);

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    Object.values(sections).forEach(section => {
        if (section) section.classList.add('hidden');
    });

    const target = sections[sectionId];
    if (target) {
        target.classList.remove('hidden');
        target.focus();
    }
}

// Form Handling
function setupForm() {
    scenarioForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await createScenarioAndPlan();
    });
}

async function createScenarioAndPlan() {
    const formData = new FormData(scenarioForm);

    const scenarioData = {
        incident_type: formData.get('incident_type'),
        severity_level: parseInt(formData.get('severity_level')),
        location: formData.get('location'),
        affected_area_radius: parseFloat(formData.get('affected_area_radius')),
        estimated_population_affected: parseInt(formData.get('estimated_population_affected')),
        duration_hours: parseInt(formData.get('duration_hours'))
    };

    // Add coordinates if provided
    const lat = formData.get('lat');
    const lon = formData.get('lon');
    if (lat && lon) {
        scenarioData.coordinates = [parseFloat(lat), parseFloat(lon)];
    }

    // Show loading
    showLoading(true);
    planResultsEl.classList.add('hidden');

    try {
        // Create scenario
        const createResponse = await fetch(`${API_BASE}/scenarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scenarioData)
        });

        if (!createResponse.ok) {
            throw new Error('Failed to create scenario');
        }

        const scenario = await createResponse.json();

        // Generate plan
        const planResponse = await fetch(`${API_BASE}/scenarios/${scenario.id}/plan`, {
            method: 'POST'
        });

        if (!planResponse.ok) {
            throw new Error('Failed to generate plan');
        }

        const plan = await planResponse.json();

        // Display results
        displayPlan(plan, scenarioData);

        // Load additional data
        if (lat && lon) {
            await loadWeather(parseFloat(lat), parseFloat(lon));
        }
        await loadEvacuationRoutes();

    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayPlan(plan, scenario) {
    // Summary
    document.getElementById('plan-summary').innerHTML = `
        <div class="card">
            <div class="card-header">Plan Summary</div>
            <p><strong>Scenario:</strong> ${scenario.incident_type.toUpperCase()} - Severity ${scenario.severity_level}</p>
            <p><strong>Location:</strong> ${scenario.location}</p>
            <p><strong>Population Affected:</strong> ${scenario.estimated_population_affected.toLocaleString()}</p>
            <p><strong>Duration:</strong> ${scenario.duration_hours} hours</p>
            <p><strong>Estimated Cost:</strong> $${plan.estimated_cost?.toLocaleString() || 'N/A'}</p>
            <p><strong>Processing Time:</strong> ${plan.processing_time_ms}ms</p>
        </div>
    `;

    // Agencies
    const agencyBadges = plan.supporting_agencies.map(a =>
        `<span class="badge badge-secondary">${a}</span>`
    ).join('');

    document.getElementById('plan-agencies').innerHTML = `
        <div class="card">
            <div class="card-header">Agency Coordination</div>
            <p><strong>Lead Agency:</strong> <span class="badge badge-primary">${plan.lead_agency}</span></p>
            <p><strong>Supporting Agencies:</strong></p>
            <div>${agencyBadges}</div>
        </div>
    `;

    // Resources
    document.getElementById('plan-resources').innerHTML = `
        <div class="card">
            <div class="card-header">Resources Allocated</div>
            <table>
                <tr><th>Resource</th><th>Quantity</th></tr>
                <tr><td>Personnel</td><td>${plan.personnel_count.toLocaleString()}</td></tr>
                <tr><td>Vehicles</td><td>${plan.vehicle_count.toLocaleString()}</td></tr>
            </table>
            <p><strong>Equipment:</strong> ${plan.equipment_list.join(', ')}</p>
        </div>
    `;

    // Timeline
    const timelineItems = plan.timeline_milestones.map(m => `
        <div class="timeline-item">
            <div class="timeline-time">${m.target_time_hours}h - ${m.phase}</div>
            <div class="timeline-content">${m.action}</div>
        </div>
    `).join('');

    document.getElementById('plan-timeline').innerHTML = `
        <div class="card">
            <div class="card-header">Response Timeline</div>
            <div class="timeline">${timelineItems}</div>
        </div>
    `;

    // Actions
    const actionItems = plan.immediate_actions.map(a => `<li>${a}</li>`).join('');
    document.getElementById('plan-actions').innerHTML = `
        <div class="card">
            <div class="card-header">Immediate Actions</div>
            <ul class="action-list">${actionItems}</ul>
        </div>
    `;

    planResultsEl.classList.remove('hidden');

    // Announce to screen readers
    announceToScreenReader('Response plan generated successfully');
}

// Weather
async function loadWeather(lat, lon) {
    try {
        const response = await fetch(`${API_BASE}/weather/current?lat=${lat}&lon=${lon}`);
        const weather = await response.json();

        const riskResponse = await fetch(`${API_BASE}/weather/risk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lon })
        });
        const risk = await riskResponse.json();

        const weatherSection = document.getElementById('weather-section');
        document.getElementById('weather-display').innerHTML = `
            <div class="weather-card">
                <div class="weather-stat">
                    <div class="value">${Math.round(weather.temperature_f)}°F</div>
                    <div class="label">Temperature</div>
                </div>
                <div class="weather-stat">
                    <div class="value">${Math.round(weather.wind_speed_mph)} mph</div>
                    <div class="label">Wind Speed</div>
                </div>
                <div class="weather-stat">
                    <div class="value">${Math.round(weather.humidity_percent)}%</div>
                    <div class="label">Humidity</div>
                </div>
                <div class="weather-stat">
                    <div class="value">${weather.conditions}</div>
                    <div class="label">Conditions</div>
                </div>
            </div>
            <div class="card" style="margin-top: 16px;">
                <div class="card-header">Risk Assessment</div>
                <p><strong>Wind Risk:</strong> <span class="risk-${risk.risk_assessment.wind_risk}">${risk.risk_assessment.wind_risk}</span></p>
                <p><strong>Temperature Risk:</strong> <span class="risk-${risk.risk_assessment.temperature_risk}">${risk.risk_assessment.temperature_risk}</span></p>
                <p><strong>Overall Risk:</strong> <span class="risk-${risk.risk_assessment.overall_risk}">${risk.risk_assessment.overall_risk.toUpperCase()}</span></p>
            </div>
        `;

        weatherSection.classList.remove('hidden');
    } catch (error) {
        console.error('Weather error:', error);
    }
}

// Evacuation Routes
async function loadEvacuationRoutes() {
    try {
        const response = await fetch(`${API_BASE}/evacuation/routes?zone=zone_a`);
        const data = await response.json();

        const routeRows = data.routes.map(r => `
            <tr>
                <td>${r.name}</td>
                <td>${r.distance_miles} mi</td>
                <td>${r.estimated_time_minutes} min</td>
                <td>${r.capacity_per_hour.toLocaleString()}/hr</td>
                <td><span class="badge ${r.status === 'available' ? 'badge-success' : 'badge-warning'}">${r.status}</span></td>
            </tr>
        `).join('');

        document.getElementById('evacuation-routes').innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Distance</th>
                        <th>Est. Time</th>
                        <th>Capacity</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>${routeRows}</tbody>
            </table>
        `;

        document.getElementById('evacuation-section').classList.remove('hidden');
    } catch (error) {
        console.error('Evacuation routes error:', error);
    }
}

// Historical Search
document.getElementById('search-btn')?.addEventListener('click', searchHistorical);
document.getElementById('historical-query')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchHistorical();
});

async function searchHistorical() {
    const query = document.getElementById('historical-query').value;

    try {
        const response = await fetch(`${API_BASE}/historical/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        const results = data.results.map(r => `
            <div class="card">
                <div class="card-header">${r.incident_type.toUpperCase()} - ${r.date.split('T')[0]}</div>
                <p><strong>Location:</strong> ${r.location}</p>
                <p><strong>Severity:</strong> ${r.severity}/5</p>
                <p><strong>Affected:</strong> ${r.affected_population.toLocaleString()}</p>
                <p><strong>Outcome:</strong> ${r.outcome}</p>
                <p><strong>Key Lesson:</strong> ${r.lessons_learned[0]}</p>
            </div>
        `).join('');

        document.getElementById('historical-results').innerHTML = results || '<p>No results found.</p>';
        document.getElementById('historical-section').classList.remove('hidden');
    } catch (error) {
        console.error('Historical search error:', error);
    }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Alt + 1-4 for section navigation
        if (e.altKey && e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            const sectionMap = {
                '1': 'scenario-section',
                '2': 'weather-section',
                '3': 'evacuation-section',
                '4': 'historical-section'
            };
            const sectionId = sectionMap[e.key];
            showSection(sectionId);

            // Update nav
            navLinks.forEach(link => {
                if (link.getAttribute('href') === '#' + sectionId) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        // Escape to close results
        if (e.key === 'Escape') {
            planResultsEl.classList.add('hidden');
        }
    });
}

// Utility Functions
function showLoading(show) {
    loadingEl.classList.toggle('hidden', !show);
    document.getElementById('create-btn').disabled = show;
}

function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);

    setTimeout(() => announcement.remove(), 1000);
}
