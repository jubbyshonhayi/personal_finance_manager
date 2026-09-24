document.addEventListener("DOMContentLoaded", () => {
    const currencySelect = document.getElementById("currency");
    const periodSelect = document.getElementById("period");

    if (!currencySelect && !periodSelect) {
        return;
    }

    const filterSelects = [
        currencySelect,
        periodSelect
    ].filter(Boolean);

    filterSelects.forEach((select) => {
        select.addEventListener("change", () => {
            select.form.submit();
        });
    });
});
