/* ============================================
   ADMIN DASHBOARD FUNCTIONALITY
   ============================================ */

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab
    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Activate selected nav item
    event.target.classList.add('active');
}

/**
 * Open add game modal
 */
function openAddGameModal() {
    const modal = document.getElementById('add-game-modal');
    modal.classList.remove('hidden');
    modal.classList.add('active');
}

/**
 * Close modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('hidden');
    modal.classList.remove('active');
}

/**
 * Handle add game form submission
 */
const addGameForm = document.getElementById('add-game-form');
if (addGameForm) {
    addGameForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            title: document.getElementById('game-title').value,
            genre: document.getElementById('game-genre').value,
            description: document.getElementById('game-description').value,
            cover_image_url: document.getElementById('game-cover').value,
            download_link: document.getElementById('game-link').value
        };
        
        try {
            const response = await fetch('/admin/api/game/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast(data.message, 'success');
                closeModal('add-game-modal');
                addGameForm.reset();
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error adding game', 'error');
        }
    });
}

/**
 * Edit game (placeholder for full implementation)
 */
function editGame(gameId) {
    showToast('Edit feature coming soon', 'info');
}

/**
 * Delete game
 */
async function deleteGame(gameId) {
    if (!confirm('Are you sure you want to delete this game?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/api/game/${gameId}/delete`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error deleting game', 'error');
    }
}

/**
 * Update request status
 */
async function updateRequestStatus(requestId, newStatus) {
    try {
        const response = await fetch(`/admin/api/request/${requestId}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error updating request', 'error');
    }
}

/**
 * Close modal when clicking outside
 */
document.addEventListener('click', (e) => {
    const modals = document.querySelectorAll('.modal.active');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            modal.classList.remove('active');
        }
    });
});

/**
 * Handle Escape key to close modals
 */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.add('hidden');
            modal.classList.remove('active');
        });
    }
});