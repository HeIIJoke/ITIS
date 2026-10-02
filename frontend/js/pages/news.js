function initNewsPage() {
    const toggleBtn = document.getElementById('toggle-form-btn');
    const cancelBtn = document.getElementById('cancel-form-btn');
    const formCard = document.getElementById('publish-form-card');

    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        formCard.classList.toggle('hidden');
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            formCard.classList.add('hidden');
        });
    }
}