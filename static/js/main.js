// ── Toast Notifications ──
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : '✕'}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ── Auto dismiss django messages ──
document.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.toast');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => msg.remove(), 300);
        }, 3000);
    });
});

// ── Live Search ──
const searchInput = document.getElementById('search-input');
if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            searchInput.closest('form').submit();
        }, 400);
    });
}

// ── Bulk Delete ──
const selectAll = document.getElementById('select-all');
if (selectAll) {
    selectAll.addEventListener('change', () => {
        document.querySelectorAll('.student-checkbox')
            .forEach(cb => cb.checked = selectAll.checked);
        updateBulkBtn();
    });
}

document.querySelectorAll('.student-checkbox').forEach(cb => {
    cb.addEventListener('change', updateBulkBtn);
});

function updateBulkBtn() {
    const checked = document.querySelectorAll('.student-checkbox:checked').length;
    const btn = document.getElementById('bulk-delete-btn');
    if (btn) {
        btn.style.display = checked > 0 ? 'inline-flex' : 'none';
        btn.textContent = `Delete Selected (${checked})`;
    }
}

function bulkDelete() {
    const checked = [...document.querySelectorAll('.student-checkbox:checked')]
        .map(cb => cb.value);
    if (checked.length === 0) return;
    if (!confirm(`Delete ${checked.length} student(s)? This can't be undone.`)) return;

    fetch('/api/students/bulk_delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ ids: checked }),
    })
    .then(res => res.json())
    .then(data => {
        showToast(data.message || 'Deleted successfully');
        setTimeout(() => location.reload(), 800);
    })
    .catch(() => showToast('Something went wrong', 'error'));
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}