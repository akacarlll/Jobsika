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
    // This is the URL for your disconnect view

    fetch(disconnectEndpointUrl, {
      method: 'GET', // or 'GET', depending on your view's configuration
      headers: {
        'X-CSRFToken': '{{ csrf_token }}'
      }
    })
    .then(response => {
      // Check if the server's response indicates a successful disconnection
      if (response.redirected) {
        // If the server sent a redirect response, follow it
        window.location.href = response.url;
      } else {
        // If not, simply reload the page
        location.reload();
      }
    })
    .catch(error => {
      console.error('Erreur lors de la déconnexion:', error);
      location.reload();
    });
  }
}