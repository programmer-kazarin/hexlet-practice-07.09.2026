document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});

async function loadHistory() {
    const wrapper = document.getElementById("historyWrapper");
    const container = document.getElementById("historyContainer");
    const partnerId = wrapper.dataset.partnerId;

    try {
        const response = await fetch(`/api/partners/${partnerId}/history`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Не удалось загрузить историю продаж");
        }
        renderHistory(container, data);

    } catch (loadError) {
        console.error("Ошибка загрузки истории продаж:", loadError);
        showErrorDialog(
            `${loadError.message}. Проверьте подключение к серверу и обновите страницу.`
        );
        container.replaceChildren(createMessage("Не удалось загрузить данные"));
    }
}

function renderHistory(container, history) {
    const sales = history.sales;

    if (!Array.isArray(sales) || sales.length === 0) {
        container.replaceChildren(
            createMessage("У этого партнера пока нет реализованной продукции")
        );
        return;
    }

    const table = document.createElement("table");
    table.className = "history-table";

    const thead = table.createTHead();
    const headRow = thead.insertRow();
    [
        { text: "Наименование продукции", numeric: false },
        { text: "Количество (шт.)", numeric: true },
        { text: "Дата продажи", numeric: false },
    ].forEach(({ text, numeric }) => {
        const th = document.createElement("th");
        th.textContent = text;
        if (numeric) th.className = "cell-number";
        headRow.appendChild(th);
    });

    const tbody = table.createTBody();
    sales.forEach((sale) => {
        const row = tbody.insertRow();
        row.insertCell().textContent = sale.product_name;

        const quantityCell = row.insertCell();
        quantityCell.className = "cell-number";
        quantityCell.textContent = formatNumber(sale.quantity);

        row.insertCell().textContent = sale.sale_date;
    });

    const tfoot = table.createTFoot();
    const footRow = tfoot.insertRow();
    footRow.insertCell().textContent = "Итого";
    const totalCell = footRow.insertCell();
    totalCell.className = "cell-number";
    totalCell.textContent = formatNumber(history.total_quantity);
    footRow.insertCell();

    container.replaceChildren(table);
}

function formatNumber(value) {
    return Number(value).toLocaleString("ru-RU");
}

function createMessage(text) {
    const message = document.createElement("p");
    message.className = "loading-state";
    message.textContent = text;
    return message;
}