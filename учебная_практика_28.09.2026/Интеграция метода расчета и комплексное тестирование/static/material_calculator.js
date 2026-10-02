const INTEGER_PATTERN = /^\d+$/;
const NUMBER_PATTERN = /^\d+(?:[.,]\d+)?$/;

const FIELD_LABELS = {
    productTypeId: "ID типа продукции",
    materialTypeId: "ID типа материала",
    quantity: "Количество продукции",
    param1: "Параметр 1",
    param2: "Параметр 2",
};

/** Ошибка "расчет невозможен": сервер вернул 422, то есть метод вернул -1. */
class CalculationUnavailableError extends Error {}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("calculatorForm");
    form.addEventListener("submit", handleCalculate);
});

async function handleCalculate(event) {
    event.preventDefault();

    const inputs = collectInputs();
    const validationMessage = validateInputs(inputs);
    if (validationMessage !== null) {
        showErrorDialog(validationMessage);
        return;
    }

    setCalculating(true);
    clearResult();

    try {
        const payload = toPayload(inputs);
        const response = await fetch("/api/calculate-material", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();

        if (response.status === 422) {
            throw new CalculationUnavailableError(data.error || "Расчет невозможен");
        }

        if (!response.ok) {
            throw new Error(data.error || "Не удалось выполнить расчет");
        }

        renderResult(payload, data.result);
    } catch (calculationError) {
        console.error("Ошибка расчета материалов:", calculationError);
        if (calculationError instanceof CalculationUnavailableError) {
            showErrorDialog(`Метод расчета вернул -1. ${calculationError.message}`);
        } else {
            showErrorDialog(`${calculationError.message}. Проверьте подключение к серверу.`);
        }
    } finally {
        setCalculating(false);
    }
}

function collectInputs() {
    return {
        productTypeId: readField("productTypeId"),
        materialTypeId: readField("materialTypeId"),
        quantity: readField("quantity"),
        param1: readField("param1"),
        param2: readField("param2"),
    };
}

function readField(elementId) {
    const element = document.getElementById(elementId);
    return element.value.trim();
}

function toPayload(inputs) {
    return {
        product_type_id: Number(inputs.productTypeId),
        material_type_id: Number(inputs.materialTypeId),
        quantity: Number(inputs.quantity),
        param_1: Number(inputs.param1.replace(",", ".")),
        param_2: Number(inputs.param2.replace(",", ".")),
    };
}

/** Возвращает текст ошибки или null, если данные корректны. */
function validateInputs(inputs) {
    const integerFields = ["productTypeId", "materialTypeId", "quantity"];
    for (const field of integerFields) {
        if (!isPositiveInteger(inputs[field])) {
            return `Поле «${FIELD_LABELS[field]}» должно быть целым положительным числом`;
        }
    }

    const numberFields = ["param1", "param2"];
    for (const field of numberFields) {
        if (!isPositiveNumber(inputs[field])) {
            return `Поле «${FIELD_LABELS[field]}» должно быть положительным числом`;
        }
    }

    return null;
}

function isPositiveInteger(rawValue) {
    if (!INTEGER_PATTERN.test(rawValue)) {
        return false;
    }
    return Number(rawValue) > 0;
}

function isPositiveNumber(rawValue) {
    if (!NUMBER_PATTERN.test(rawValue)) {
        return false;
    }
    return Number(rawValue.replace(",", ".")) > 0;
}

function renderResult(payload, result) {
    const panel = document.getElementById("resultPanel");
    const valueField = document.getElementById("resultValue");
    const detailsField = document.getElementById("resultDetails");

    valueField.textContent = `${formatNumber(result)} шт.`;
    detailsField.textContent =
        `Тип продукции ID ${payload.product_type_id}, тип материала ID ${payload.material_type_id}, ` +
        `количество ${formatNumber(payload.quantity)} шт., параметры ${payload.param_1} и ${payload.param_2}.`;

    panel.hidden = false;
}

function clearResult() {
    const panel = document.getElementById("resultPanel");
    panel.hidden = true;
    document.getElementById("resultValue").textContent = "";
    document.getElementById("resultDetails").textContent = "";
}

function setCalculating(isCalculating) {
    const button = document.getElementById("calculateButton");
    button.disabled = isCalculating;
    button.textContent = isCalculating ? "Расчет..." : "Рассчитать";
}

function formatNumber(value) {
    return Number(value).toLocaleString("ru-RU");
}