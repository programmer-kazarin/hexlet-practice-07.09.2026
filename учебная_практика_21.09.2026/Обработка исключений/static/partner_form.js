class ValidationError extends Error {}

let initialFormSnapshot = "";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("partnerForm");
    const backLink = document.getElementById("backLink");

    // Снимок исходного состояния формы - используется, чтобы понять,
    // менял ли пользователь поля перед уходом (для Warning-диалога)
    initialFormSnapshot = JSON.stringify(collectFormData());

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        handleSavePartner(form);
    });

    backLink.addEventListener("click", (event) => {
        event.preventDefault();
        handleBackNavigation(backLink.href);
    });
});

/** Проверяет, отличаются ли текущие значения формы от исходных. */
function isFormDirty() {
    return JSON.stringify(collectFormData()) !== initialFormSnapshot;
}

/** Обработка ухода со страницы: предупреждаем о потере несохраненных данных. */
function handleBackNavigation(targetUrl) {
    if (isFormDirty()) {
        showWarningDialog(
            "Вы изменили данные в форме. При переходе назад все несохраненные " +
            "изменения будут потеряны без возможности восстановления.",
            () => { window.location.href = targetUrl; }
        );
    } else {
        window.location.href = targetUrl;
    }
}

/**
 * Валидация рейтинга: должно быть целое неотрицательное число.
 * try...catch перехватывает как явный NaN, так и любые непредвиденные
 * ошибки парсинга (например, экзотические Unicode-символы в поле).
 */
function validateRating(rawValue) {
    try {
        if (rawValue.trim() === "") {
            return 0;
        }
        const numericValue = Number(rawValue);
        if (!Number.isInteger(numericValue) || numericValue < 0) {
            throw new ValidationError("invalid rating");
        }
        return numericValue;
    } catch (parseError) {
        throw new ValidationError(
            "Рейтинг должен быть целым числом от 0. " +
            "Пожалуйста, удалите знаки препинания и повторите попытку."
        );
    }
}

/** Проверка обязательных полей. Порядок соответствует порядку полей в форме. */
function validateRequiredFields(payload) {
    if (!payload.company_name) {
        throw new ValidationError(
            "Поле «Наименование» не заполнено. " +
            "Пожалуйста, укажите название компании и повторите попытку."
        );
    }
    if (!payload.inn) {
        throw new ValidationError(
            "Поле «ИНН» не заполнено. " +
            "Пожалуйста, укажите ИНН партнера (10 или 12 цифр) и повторите попытку."
        );
    }
    if (!payload.partner_type) {
        throw new ValidationError(
            "Поле «Тип партнера» не заполнено. " +
            "Пожалуйста, выберите тип партнера из списка и повторите попытку."
        );
    }
    if (!payload.contact_email) {
        throw new ValidationError(
            "Поле «Email компании» не заполнено. " +
            "Пожалуйста, укажите адрес электронной почты и повторите попытку."
        );
    }
}

async function handleSavePartner(form) {
    const saveButton = document.getElementById("saveButton");
    const mode = form.dataset.mode;
    const partnerId = document.getElementById("partnerId").value;

    let payload;
    try {
        const ratingValue = validateRating(document.getElementById("rating").value);
        payload = collectFormData();
        payload.rating = ratingValue;
        validateRequiredFields(payload);
    } catch (validationError) {
        if (validationError instanceof ValidationError) {
            showErrorDialog(validationError.message);
        } else {
            showErrorDialog("Произошла непредвиденная ошибка при проверке данных.");
        }
        return;
    }

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
            // 503 - СУБД недоступна, 409 - дубликат ИНН, 400/404 - прочие ошибки сервера
            throw new Error(result.error || "Не удалось сохранить партнера.");
        }

        initialFormSnapshot = JSON.stringify(payload); // форма больше не "грязная"

        showInfoDialog(
            mode === "edit"
                ? "Данные партнера успешно обновлены."
                : "Новый партнер успешно добавлен в базу.",
            () => { window.location.href = "/"; }
        );

    } catch (saveError) {
        console.error("Ошибка сохранения партнера:", saveError);
        showErrorDialog(
            `${saveError.message} Проверьте подключение к сети и повторите попытку.`
        );
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

function setSaving(button, isSaving) {
    button.disabled = isSaving;
    button.textContent = isSaving ? "Сохранение..." : "Сохранить";
}