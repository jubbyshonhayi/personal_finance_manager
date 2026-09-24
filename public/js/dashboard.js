document.addEventListener("DOMContentLoaded", () => {
    const currencySelect = document.getElementById("currency");
    const periodSelect = document.getElementById("period");

    if (currencySelect || periodSelect) {
        const filterSelects = [
            currencySelect,
            periodSelect
        ].filter(Boolean);

        filterSelects.forEach((select) => {
            select.addEventListener("change", () => {
                select.form.submit();
            });
        });
    }

    const progressBars =
        document.querySelectorAll(".budget-progress-bar");

    for (const progressBar of progressBars) {
        const progress = Number(progressBar.dataset.progress);

        if (Number.isFinite(progress)) {
            progressBar.style.width = `${Math.min(progress, 100)}%`;
        }
    }
});
