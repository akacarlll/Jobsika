let isUrlMode = true; // Track current mode (true = URL mode, false = description mode)

function toggleSubmitType() {
    const urlSection = document.getElementById('urlSection');
    const descriptionSection = document.getElementById('descriptionSection');
    const toggleButton = document.getElementById('change_submit_type');
    const formTitle = document.getElementById('formTitle');
    const jobUrlInput = document.getElementById('job_url');
    const jobDescriptionInput = document.getElementById('job_description');
    
    if (isUrlMode) {
        // Switch to description mode
        urlSection.classList.add('hidden');
        descriptionSection.classList.remove('hidden');
        toggleButton.textContent = '🔗 Saisie par URL';
        formTitle.textContent = '📝 Ajouter une description d\'emploi';
        
        // Remove required attribute from URL input and add to description
        jobUrlInput.removeAttribute('required');
        jobDescriptionInput.setAttribute('required', 'required');
        
        isUrlMode = false;
    } else {
        // Switch to URL mode
        descriptionSection.classList.add('hidden');
        urlSection.classList.remove('hidden');
        toggleButton.textContent = '📝 Saisie manuelle';
        formTitle.textContent = '📝 Ajouter une offre d\'emploi';
        
        // Remove required attribute from description input and add to URL
        jobDescriptionInput.removeAttribute('required');
        jobUrlInput.setAttribute('required', 'required');
        
        isUrlMode = true;
    }
}

function clearForm() {
    // Clear all form inputs
    document.getElementById('job_url').value = '';
    document.getElementById('job_description').value = '';
    document.getElementById('notes').value = '';
}

// Initialize the form with URL mode and required attribute
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('job_url').setAttribute('required', 'required');
});


function disconnect() {
    if (confirm('Voulez-vous vraiment vous déconnecter de Google ?')) {
        fetch('{% url "jobs_engine:disconnect" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(() => {
            location.reload();
        })
        .catch(error => {
            console.error('Erreur lors de la déconnexion:', error);
            location.reload();
        });
    }
}

function resetButton() {
    const loading = document.getElementById('loading');
    const btn = document.getElementById('googleAuthBtn');
    const overlay = document.getElementById('popupOverlay');
    
    loading.style.display = 'none';
    btn.disabled = false;
    btn.innerHTML = `
        <div class="google-icon">
            <svg width="14" height="14" viewBox="0 0 24 24">
                <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
        </div>
        Se connecter avec Google
    `;
    overlay.style.display = 'none';
}