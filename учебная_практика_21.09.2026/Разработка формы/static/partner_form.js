document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("partnerForm");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        handleSavePartner();
    });
});

function handleSavePartner() {
    const formData = collectFormData();
    // TODO backend
    console.log("Заглушка: сохранение партнера пока не реализовано.", formData);
}

function collectFormData() {
    return {
        partner_id: document.getElementById("partnerId").value || null,
        company_name: document.getElementById("companyName").value,
        partner_type: document.getElementById("partnerType").value,
        rating: document.getElementById("rating").value,
        address: document.getElementById("address").value,
        director_name: document.getElementById("directorName").value,
        phone: document.getElementById("phone").value,
        company_email: document.getElementById("companyEmail").value,
    };
}