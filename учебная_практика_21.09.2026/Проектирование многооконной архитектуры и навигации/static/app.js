document.addEventListener("DOMContentLoaded", () => {
    loadPartners();
});

async function loadPartners() {
    const container = document.getElementById("partnersContainer");

    try {
        const response = await fetch("/api/partners");

        if (!response.ok) {
            throw new Error(`Сервер вернул статус ${response.status}`);
        }

        const partners = await response.json();
        renderPartners(container, partners);

    } catch (fetchError) {
        console.error("Ошибка загрузки партнеров:", fetchError);
        renderErrorState(container);
    }
}

function renderPartners(container, partners) {
    container.innerHTML = "";

    if (!partners || partners.length === 0) {
        renderEmptyState(container);
        return;
    }

    partners.forEach((partner) => {
        const card = createPartnerCard(partner);
        container.appendChild(card);
    });
}

function createPartnerCard(partner) {
    const { orgType, orgName } = splitCompanyType(partner.company_name);

    const card = document.createElement("div");
    card.className = "partner-card";

    const topRow = document.createElement("div");
    topRow.className = "partner-card__top";

    const titleSpan = document.createElement("span");
    titleSpan.className = "partner-card__title";
    titleSpan.textContent = `${orgType} | ${orgName}`;

    const discountSpan = document.createElement("span");
    discountSpan.className = "partner-card__discount";
    const discountPercent = partner.discount_percent ?? 0;
    discountSpan.textContent = `${discountPercent}%`;

    topRow.appendChild(titleSpan);
    topRow.appendChild(discountSpan);
    card.appendChild(topRow);

    const contactText = partner.contact_email || "Контакт не указан";
    card.appendChild(createInfoLine(contactText));

    const phoneText = partner.phone || "Телефон не указан";
    card.appendChild(createInfoLine(phoneText));

    const ratingValue = partner.rating;
    const ratingText = ratingValue !== null && ratingValue !== undefined
        ? `Рейтинг: ${ratingValue}`
        : "Рейтинг: —";
    card.appendChild(createInfoLine(ratingText));

    return card;
}

function createInfoLine(text) {
    const paragraph = document.createElement("p");
    paragraph.className = "partner-card__info";
    paragraph.textContent = text;
    return paragraph;
}

function splitCompanyType(companyName) {
    if (!companyName) {
        return { orgType: "Партнер", orgName: "Без названия" };
    }

    const match = companyName.trim().match(/^(ООО|ИП|ЗАО|ОАО|ТК)\s+(.*)/);
    if (match) {
        const orgName = match[2].replace(/^"|"$/g, "").trim();
        return { orgType: match[1], orgName };
    }

    return { orgType: "Партнер", orgName: companyName.trim() };
}

function renderEmptyState(container) {
    container.innerHTML = "";
    const emptyParagraph = document.createElement("p");
    emptyParagraph.className = "empty-state";
    emptyParagraph.textContent = "Нет данных о партнерах";
    container.appendChild(emptyParagraph);
}

function renderErrorState(container) {
    container.innerHTML = "";
    const errorParagraph = document.createElement("p");
    errorParagraph.className = "error-state";
    errorParagraph.textContent = "Не удалось загрузить данные партнеров. Проверьте подключение к серверу.";
    container.appendChild(errorParagraph);
}