document.addEventListener("DOMContentLoaded", () => {
    const currencySelect = document.getElementById("currency");

    if (!currencySelect) {
        return;
    }

    currencySelect.addEventListener("change", () => {
        currencySelect.form.submit();
    });
});