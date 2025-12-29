/* ============================================
   LANDING PAGE FUNCTIONALITY
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Handle request game form
    const requestForm = document.getElementById('request-form');
    if (requestForm) {
        requestForm.addEventListener('submit', handleGameRequest);
    }
});

/**
 * Handle game request submission
 */
async function handleGameRequest(event) {
    event.preventDefault();
    
    const gameTitle = document.getElementById('game-title').value.trim();
    const userEmail = document.getElementById('user-email').value.trim();
    
    // Validation
    if (!gameTitle || gameTitle.length < 2) {
        showToast('Please enter a game title', 'error');
        return;
    }
    
    if (userEmail && !validateEmail(userEmail)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    try {
        const response = await fetch('/request-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                game_title: gameTitle,
                user_email: userEmail || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showToast(data.message, 'success');
            document.getElementById('request-form').reset();
        } else {
            showToast(data.message || 'Error submitting request', 'error');
        }
    } catch (error) {
        console.error('Request error:', error);
        showToast('Error submitting request. Please try again.', 'error');
    }
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

/**
 * Download game
 */
function downloadGame(event, gameId) {
    event.preventDefault();
    event.stopPropagation();
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Opening...';
    
    fetch(`/api/games/${gameId}`)
        .then(response => response.json())
        .then(game => {
            // Open download link in new tab
            window.open(game.download_link, '_blank');
            btn.disabled = false;
            btn.textContent = 'Download';
            showToast('Download started!', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            btn.disabled = false;
            btn.textContent = 'Download';
            showToast('Error retrieving download link', 'error');
        });
}
