const DIALOG_ICONS = {
    error: `<svg viewBox="0 0 24 24" width="28" height="28">
                <circle cx="12" cy="12" r="11" fill="#c0392b"/>
                <line x1="7" y1="7" x2="17" y2="17" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
                <line x1="17" y1="7" x2="7" y2="17" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
            </svg>`,
    warning: `<svg viewBox="0 0 24 24" width="28" height="28">
                <polygon points="12,2 22,21 2,21" fill="#e6a700"/>
                <rect x="11" y="9" width="2" height="6" fill="#fff"/>
                <rect x="11" y="16" width="2" height="2" fill="#fff"/>
            </svg>`,
    info: `<svg viewBox="0 0 24 24" width="28" height="28">
                <circle cx="12" cy="12" r="11" fill="#2a6fdb"/>
                <rect x="11" y="10" width="2" height="7" fill="#fff"/>
                <rect x="11" y="6" width="2" height="2" fill="#fff"/>
            </svg>`,
};

const DIALOG_TITLES = {
    error: "Ошибка",
    warning: "Предупреждение",
    info: "Информация",
};

/**
 * Универсальный показ модального окна.
 * onConfirm/onCancel - колбэки, вызываются после закрытия соответствующей кнопкой.
 */
function showDialog({
    type = "info",
    title = null,
    message,
    confirmText = "ОК",
    cancelText = null,
    onConfirm = null,
    onCancel = null,
}) {
    const overlay = document.createElement("div");
    overlay.className = "dialog-overlay";

    const box = document.createElement("div");
    box.className = `dialog-box dialog-box--${type}`;

    const header = document.createElement("div");
    header.className = "dialog-header";

    const iconWrapper = document.createElement("span");
    iconWrapper.className = "dialog-icon";
    iconWrapper.innerHTML = DIALOG_ICONS[type];

    const titleEl = document.createElement("h2");
    titleEl.className = "dialog-title";
    titleEl.textContent = title || DIALOG_TITLES[type];

    header.append(iconWrapper, titleEl);

    const messageEl = document.createElement("p");
    messageEl.className = "dialog-message";
    messageEl.textContent = message;

    const actions = document.createElement("div");
    actions.className = "dialog-actions";

    const confirmBtn = document.createElement("button");
    confirmBtn.className = "btn btn-primary";
    confirmBtn.textContent = confirmText;
    confirmBtn.addEventListener("click", () => {
        overlay.remove();
        if (onConfirm) onConfirm();
    });
    actions.appendChild(confirmBtn);

    if (cancelText) {
        const cancelBtn = document.createElement("button");
        cancelBtn.className = "btn btn-secondary";
        cancelBtn.textContent = cancelText;
        cancelBtn.addEventListener("click", () => {
            overlay.remove();
            if (onCancel) onCancel();
        });
        actions.appendChild(cancelBtn);
    }

    box.append(header, messageEl, actions);
    overlay.appendChild(box);
    document.body.appendChild(overlay);

    confirmBtn.focus();
}

/** Ошибка: валидация не прошла или БД недоступна. Только кнопка "Понятно". */
function showErrorDialog(message) {
    showDialog({ type: "error", message, confirmText: "Понятно" });
}

/** Предупреждение: несохраненные данные будут потеряны. Требует подтверждения. */
function showWarningDialog(message, onConfirm, onCancel = null) {
    showDialog({
        type: "warning",
        message,
        confirmText: "Да, уйти без сохранения",
        cancelText: "Отмена",
        onConfirm,
        onCancel,
    });
}

/** Информация: операция прошла успешно. */
function showInfoDialog(message, onConfirm = null) {
    showDialog({ type: "info", message, confirmText: "ОК", onConfirm });
}