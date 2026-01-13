/**
 * Document Eligibility Agent - Queue Management Interface
 * WCAG 2.1 AA Compliant JavaScript
 */

// API Configuration
const API_BASE = '/api/v1';

// State
let currentPage = 1;
let pageSize = 20;
let totalPages = 1;
let selectedDocuments = new Set();
let currentDocumentId = null;

// DOM Elements
const elements = {
    uploadForm: document.getElementById('upload-form'),
    uploadStatus: document.getElementById('upload-status'),
    uploadBtn: document.getElementById('upload-btn'),
    queueBody: document.getElementById('queue-body'),
    queueCount: document.getElementById('queue-count'),
    statusFilter: document.getElementById('status-filter'),
    typeFilter: document.getElementById('type-filter'),
    refreshBtn: document.getElementById('refresh-btn'),
    selectAll: document.getElementById('select-all'),
    bulkActions: document.getElementById('bulk-actions'),
    selectedCount: document.getElementById('selected-count'),
    bulkApproveBtn: document.getElementById('bulk-approve-btn'),
    clearSelectionBtn: document.getElementById('clear-selection-btn'),
    prevPage: document.getElementById('prev-page'),
    nextPage: document.getElementById('next-page'),
    pageInfo: document.getElementById('page-info'),
    documentModal: document.getElementById('document-modal'),
    documentInfo: document.getElementById('document-info'),
    extractionsBody: document.getElementById('extractions-body'),
    modalApproveBtn: document.getElementById('modal-approve-btn'),
    modalRejectBtn: document.getElementById('modal-reject-btn'),
    modalCloseBtn: document.getElementById('modal-close-btn'),
    srAnnouncements: document.getElementById('sr-announcements'),
    // Stats
    statTotal: document.getElementById('stat-total'),
    statPending: document.getElementById('stat-pending'),
    statApproved: document.getElementById('stat-approved'),
    statRate: document.getElementById('stat-rate'),
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadQueue();
    loadStats();
});

// Event Listeners
function initEventListeners() {
    // Upload form
    elements.uploadForm.addEventListener('submit', handleUpload);

    // Filters
    elements.statusFilter.addEventListener('change', () => { currentPage = 1; loadQueue(); });
    elements.typeFilter.addEventListener('change', () => { currentPage = 1; loadQueue(); });
    elements.refreshBtn.addEventListener('click', loadQueue);

    // Selection
    elements.selectAll.addEventListener('change', handleSelectAll);
    elements.clearSelectionBtn.addEventListener('click', clearSelection);
    elements.bulkApproveBtn.addEventListener('click', handleBulkApprove);

    // Pagination
    elements.prevPage.addEventListener('click', () => { currentPage--; loadQueue(); });
    elements.nextPage.addEventListener('click', () => { currentPage++; loadQueue(); });

    // Modal
    elements.modalCloseBtn.addEventListener('click', closeModal);
    document.querySelector('.close-btn').addEventListener('click', closeModal);
    elements.modalApproveBtn.addEventListener('click', () => handleDocumentAction('approve'));
    elements.modalRejectBtn.addEventListener('click', () => handleDocumentAction('reject'));

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Modal backdrop click
    elements.documentModal.addEventListener('click', (e) => {
        if (e.target === elements.documentModal) closeModal();
    });
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new Error(error.message || `HTTP ${response.status}`);
    }

    if (response.status === 204) return null;
    return response.json();
}

// Upload Handler
async function handleUpload(e) {
    e.preventDefault();

    const formData = new FormData(elements.uploadForm);
    elements.uploadBtn.disabled = true;
    elements.uploadBtn.textContent = 'Uploading...';

    try {
        const result = await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            body: formData,
        });

        if (!result.ok) {
            const error = await result.json();
            throw new Error(error.message || 'Upload failed');
        }

        const doc = await result.json();
        showStatus('success', `Document uploaded successfully! ID: ${doc.id.substring(0, 8)}...`);
        announce(`Document uploaded successfully`);
        elements.uploadForm.reset();
        loadQueue();
        loadStats();
    } catch (error) {
        showStatus('error', `Upload failed: ${error.message}`);
        announce(`Upload failed: ${error.message}`);
    } finally {
        elements.uploadBtn.disabled = false;
        elements.uploadBtn.textContent = 'Upload Document';
    }
}

// Queue Loading
async function loadQueue() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize,
        });

        if (elements.statusFilter.value) {
            params.append('status', elements.statusFilter.value);
        }
        if (elements.typeFilter.value) {
            params.append('document_type', elements.typeFilter.value);
        }

        const data = await apiCall(`/queue?${params}`);
        renderQueue(data.items);
        updatePagination(data);
        elements.queueCount.textContent = data.total;
    } catch (error) {
        console.error('Failed to load queue:', error);
        elements.queueBody.innerHTML = `
            <tr><td colspan="8" class="empty-message">Failed to load queue: ${error.message}</td></tr>
        `;
    }
}

function renderQueue(documents) {
    if (!documents || documents.length === 0) {
        elements.queueBody.innerHTML = `
            <tr><td colspan="8" class="empty-message">No documents in queue</td></tr>
        `;
        return;
    }

    elements.queueBody.innerHTML = documents.map(doc => `
        <tr data-id="${doc.id}">
            <td>
                <input type="checkbox"
                       class="doc-checkbox"
                       data-id="${doc.id}"
                       aria-label="Select document ${doc.case_id}"
                       ${selectedDocuments.has(doc.id) ? 'checked' : ''}>
            </td>
            <td><strong>${escapeHtml(doc.case_id)}</strong></td>
            <td>${formatDocumentType(doc.document_type)}</td>
            <td><span class="status-badge ${doc.status}">${formatStatus(doc.status)}</span></td>
            <td>${renderConfidence(doc.overall_confidence)}</td>
            <td><span class="priority-badge ${doc.priority}">${doc.priority}</span></td>
            <td>${formatDate(doc.uploaded_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewDocument('${doc.id}')"
                        aria-label="View document ${doc.case_id}">
                    View
                </button>
            </td>
        </tr>
    `).join('');

    // Add checkbox listeners
    document.querySelectorAll('.doc-checkbox').forEach(cb => {
        cb.addEventListener('change', handleCheckboxChange);
    });
}

function renderConfidence(confidence) {
    if (confidence === null || confidence === undefined) {
        return '<span class="text-muted">-</span>';
    }

    const percent = Math.round(confidence * 100);
    let level = 'low';
    if (percent >= 85) level = 'high';
    else if (percent >= 70) level = 'medium';

    return `
        <div class="confidence">
            <div class="confidence-bar">
                <div class="confidence-fill ${level}" style="width: ${percent}%"></div>
            </div>
            <span>${percent}%</span>
        </div>
    `;
}

// Selection Handling
function handleCheckboxChange(e) {
    const id = e.target.dataset.id;
    if (e.target.checked) {
        selectedDocuments.add(id);
    } else {
        selectedDocuments.delete(id);
    }
    updateBulkActions();
}

function handleSelectAll(e) {
    const checkboxes = document.querySelectorAll('.doc-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = e.target.checked;
        if (e.target.checked) {
            selectedDocuments.add(cb.dataset.id);
        } else {
            selectedDocuments.delete(cb.dataset.id);
        }
    });
    updateBulkActions();
}

function clearSelection() {
    selectedDocuments.clear();
    document.querySelectorAll('.doc-checkbox').forEach(cb => cb.checked = false);
    elements.selectAll.checked = false;
    updateBulkActions();
}

function updateBulkActions() {
    const count = selectedDocuments.size;
    elements.selectedCount.textContent = `${count} selected`;
    elements.bulkActions.hidden = count === 0;
}

// Bulk Approve
async function handleBulkApprove() {
    if (selectedDocuments.size === 0) return;

    const ids = Array.from(selectedDocuments);
    elements.bulkApproveBtn.disabled = true;
    elements.bulkApproveBtn.textContent = 'Processing...';

    try {
        const result = await apiCall('/queue/bulk-approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document_ids: ids }),
        });

        announce(`${result.approved} documents approved, ${result.failed} failed`);
        clearSelection();
        loadQueue();
        loadStats();
    } catch (error) {
        announce(`Bulk approve failed: ${error.message}`);
    } finally {
        elements.bulkApproveBtn.disabled = false;
        elements.bulkApproveBtn.textContent = 'Approve Selected';
    }
}

// Document Modal
async function viewDocument(id) {
    currentDocumentId = id;

    try {
        const [doc, extractions] = await Promise.all([
            apiCall(`/documents/${id}`),
            apiCall(`/extractions/${id}`),
        ]);

        renderDocumentModal(doc, extractions);
        elements.documentModal.showModal();
        elements.documentModal.querySelector('.close-btn').focus();
    } catch (error) {
        announce(`Failed to load document: ${error.message}`);
    }
}

function renderDocumentModal(doc, extractionData) {
    elements.documentInfo.innerHTML = `
        <dl>
            <dt>Case ID</dt><dd>${escapeHtml(doc.case_id)}</dd>
            <dt>Document Type</dt><dd>${formatDocumentType(doc.document_type)}</dd>
            <dt>Status</dt><dd><span class="status-badge ${doc.status}">${formatStatus(doc.status)}</span></dd>
            <dt>Filename</dt><dd>${escapeHtml(doc.filename)}</dd>
            <dt>Uploaded</dt><dd>${formatDate(doc.uploaded_at)}</dd>
            <dt>Overall Confidence</dt><dd>${doc.overall_confidence ? Math.round(doc.overall_confidence * 100) + '%' : 'N/A'}</dd>
        </dl>
    `;

    const extractions = extractionData.extractions || [];
    if (extractions.length === 0) {
        elements.extractionsBody.innerHTML = `
            <tr><td colspan="4">No extractions available</td></tr>
        `;
    } else {
        elements.extractionsBody.innerHTML = extractions.map(ext => `
            <tr>
                <td><strong>${escapeHtml(ext.field_name)}</strong></td>
                <td>${escapeHtml(ext.is_pii ? (ext.display_value || '***') : ext.field_value)}</td>
                <td>${renderConfidence(ext.confidence)}</td>
                <td>${ext.validation_status ? `<span class="status-badge ${ext.validation_status}">${ext.validation_status}</span>` : '-'}</td>
            </tr>
        `).join('');
    }

    // Update button states
    const canReview = ['ready_for_review', 'extracted', 'validating'].includes(doc.status);
    elements.modalApproveBtn.disabled = !canReview;
    elements.modalRejectBtn.disabled = !canReview;
}

function closeModal() {
    elements.documentModal.close();
    currentDocumentId = null;
}

async function handleDocumentAction(action) {
    if (!currentDocumentId) return;

    try {
        if (action === 'approve') {
            await apiCall(`/documents/${currentDocumentId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            announce('Document approved');
        } else {
            const reason = prompt('Enter rejection reason:');
            if (!reason) return;

            await apiCall(`/documents/${currentDocumentId}/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason }),
            });
            announce('Document rejected');
        }

        closeModal();
        loadQueue();
        loadStats();
    } catch (error) {
        announce(`Action failed: ${error.message}`);
    }
}

// Statistics
async function loadStats() {
    try {
        const stats = await apiCall('/queue/stats');
        elements.statTotal.textContent = stats.total;
        elements.statPending.textContent = stats.by_status?.ready_for_review || 0;
        elements.statApproved.textContent = stats.by_status?.approved || 0;
        elements.statRate.textContent = Math.round((stats.auto_approved_rate || 0) * 100) + '%';
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Pagination
function updatePagination(data) {
    totalPages = Math.ceil(data.total / pageSize) || 1;
    elements.pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    elements.prevPage.disabled = currentPage <= 1;
    elements.nextPage.disabled = !data.has_more;
}

// Keyboard Shortcuts
function handleKeyboardShortcuts(e) {
    // Ignore if typing in input
    if (e.target.matches('input, textarea, select')) return;

    // Ignore if modal not open for document actions
    const modalOpen = elements.documentModal.open;

    switch (e.key.toLowerCase()) {
        case 'a':
            if (modalOpen && !elements.modalApproveBtn.disabled) {
                e.preventDefault();
                handleDocumentAction('approve');
            }
            break;
        case 'r':
            if (modalOpen && !elements.modalRejectBtn.disabled) {
                e.preventDefault();
                handleDocumentAction('reject');
            }
            break;
        case 'n':
            if (!elements.nextPage.disabled) {
                e.preventDefault();
                currentPage++;
                loadQueue();
            }
            break;
        case 'p':
            if (!elements.prevPage.disabled) {
                e.preventDefault();
                currentPage--;
                loadQueue();
            }
            break;
        case 'escape':
            if (modalOpen) {
                e.preventDefault();
                closeModal();
            }
            break;
    }
}

// Utility Functions
function formatDocumentType(type) {
    const types = {
        w2: 'W-2',
        paystub: 'Pay Stub',
        utility_bill: 'Utility Bill',
        bank_statement: 'Bank Statement',
        drivers_license: "Driver's License",
        birth_certificate: 'Birth Certificate',
        lease_agreement: 'Lease Agreement',
        other: 'Other',
    };
    return types[type] || type;
}

function formatStatus(status) {
    const statuses = {
        uploaded: 'Uploaded',
        processing: 'Processing',
        extracted: 'Extracted',
        validating: 'Validating',
        ready_for_review: 'Ready for Review',
        approved: 'Approved',
        rejected: 'Rejected',
        resubmit_requested: 'Resubmit',
        failed: 'Failed',
    };
    return statuses[status] || status;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    });
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function showStatus(type, message) {
    elements.uploadStatus.className = `status-message ${type}`;
    elements.uploadStatus.textContent = message;
    elements.uploadStatus.style.display = 'block';

    setTimeout(() => {
        elements.uploadStatus.style.display = 'none';
    }, 5000);
}

function announce(message) {
    elements.srAnnouncements.textContent = message;
    setTimeout(() => {
        elements.srAnnouncements.textContent = '';
    }, 1000);
}

// Make viewDocument available globally
window.viewDocument = viewDocument;
