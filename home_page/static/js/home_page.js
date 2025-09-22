document.getElementById("googleAuthBtn").addEventListener("click", () => {
    window.location.href = "{{ google_auth_url }}";
});