let selectedPartnerId = null;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("editButton")
        .addEventListener("click", () => openForSelectedPartner("edit"));
    document.getElementById("historyButton")
        .addEventListener("click", () => openForSelectedPartner("history"));

    loadPartners();
});

/**
 * Переход на страницу выбранного партнера.
 * partner_id передается через URL: /partners/<id>/edit или /partners/<id>/history.
 */
function openForSelectedPartner(page) {
    if (selectedPartnerId === null) {
        showErrorDialog(
            "Партнер не выбран. Пожалуйста, выберите партнера в списке и повторите попытку."
        );
        return;
    }
    window.location.href = `/partners/${selectedPartnerId}/${page}`;
}

async function loadPartners() {
    const container = document.getElementById("partnersContainer");
    selectedPartnerId = null;

    try {
        const response = await fetch("/api/partners");
        const data = await response.json();

        if (!response.ok) {
            // 503 - СУБД недоступна, показываем Error-диалог вместо пустого списка
            throw new Error(data.error || "Не удалось загрузить список партнеров");
        }

        renderPartners(container, data);

    } catch (loadError) {
        console.error("Ошибка загрузки партнеров:", loadError);
        showErrorDialog(
            `${loadError.message}. Проверьте подключение к серверу и обновите страницу.`
        );
        container.innerHTML = '<p class="loading-state">Не удалось загрузить данные</p>';
    }
}

function renderPartners(container, partners) {
    container.innerHTML = "";

    if (!Array.isArray(partners) || partners.length === 0) {
        container.innerHTML = '<p class="loading-state">Партнеры не найдены</p>';
        return;
    }

    partners.forEach((partner) => {
        const card = createPartnerCard(partner);
        container.appendChild(card);
    });
}

/** Выделяет карточку выбранного партнера и снимает выделение с остальных. */
function selectPartner(card, partnerId) {
    document.querySelectorAll(".partner-card--selected").forEach((element) => {
        element.classList.remove("partner-card--selected");
        element.setAttribute("aria-selected", "false");
    });
    card.classList.add("partner-card--selected");
    card.setAttribute("aria-selected", "true");
    selectedPartnerId = partnerId;
}

function createPartnerCard(partner) {
    const { orgType, orgName } = splitCompanyType(partner.company_name);

    const card = document.createElement("div");
    card.className = "partner-card";
    card.tabIndex = 0;
    card.setAttribute("aria-selected", "false");

    // Одинарный клик - выбор партнера, двойной - открытие карточки редактирования
    card.addEventListener("click", () => selectPartner(card, partner.partner_id));
    card.addEventListener("dblclick", () => {
        window.location.href = `/partners/${partner.partner_id}/edit`;
    });
    card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            selectPartner(card, partner.partner_id);
        }
    });

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
        : "Рейтинг: -";
    card.appendChild(createInfoLine(ratingText));

    return card;
}

function createInfoLine(text) {
    const line = document.createElement("div");
    line.className = "partner-card__line";
    line.textContent = text;
    return line;
}

function splitCompanyType(companyName) {
    if (!companyName) {
        return { orgType: "", orgName: "" };
    }

    const knownTypes = ["ООО", "ЗАО", "ОАО", "ИП", "ТК"];
    const foundType = knownTypes.find((type) => companyName.startsWith(type));

    if (foundType) {
        return {
            orgType: foundType,
            orgName: companyName.slice(foundType.length).trim(),
        };
    }

    return { orgType: "", orgName: companyName };
}