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
        inn: document.getElementById("inn").value,
        contact_email: document.getElementById("contactEmail").value,
        phone: document.getElementById("phone").value,
        rating: document.getElementById("rating").value,
    };
}