document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("partnerForm");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        handleSavePartner(form);
    });
});

async function handleSavePartner(form) {
    const saveButton = document.getElementById("saveButton");
    const errorBox = document.getElementById("formError");
    hideError(errorBox);

    const mode = form.dataset.mode;            // "add" или "edit" - передано сервером
    const partnerId = document.getElementById("partnerId").value;
    const payload = collectFormData();

    // В режиме "add" шлем POST на коллекцию, в режиме "edit" - PUT на конкретный ID.
    const url = mode === "edit" ? `/api/partners/${partnerId}` : "/api/partners";
    const method = mode === "edit" ? "PUT" : "POST";

    setSaving(saveButton, true);

    try {
        const response = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (!response.ok) {
            // 409 - дубликат ИНН, 400 - не заполнены обязательные поля,
            // 404 - партнер удален другим менеджером до сохранения
            throw new Error(result.error || "Не удалось сохранить партнера");
        }

        window.location.href = "/";

    } catch (saveError) {
        console.error("Ошибка сохранения партнера:", saveError);
        showError(errorBox, saveError.message);
    } finally {
        setSaving(saveButton, false);
    }
}

function collectFormData() {
    return {
        company_name: document.getElementById("companyName").value.trim(),
        inn: document.getElementById("inn").value.trim(),
        partner_type: document.getElementById("partnerType").value,
        rating: Number(document.getElementById("rating").value) || 0,
        address: document.getElementById("address").value.trim(),
        director_name: document.getElementById("directorName").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        contact_email: document.getElementById("companyEmail").value.trim(),
    };
}

function showError(errorBox, message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
}

function hideError(errorBox) {
    errorBox.hidden = true;
    errorBox.textContent = "";
}

function setSaving(button, isSaving) {
    button.disabled = isSaving;
    button.textContent = isSaving ? "Сохранение..." : "Сохранить";
}