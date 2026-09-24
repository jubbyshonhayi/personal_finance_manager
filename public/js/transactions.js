document.addEventListener("DOMContentLoaded", () => {
    const transactionType = document.getElementById("transaction_type");
    const categorySelect = document.getElementById("category_id");
    const transactionDate = document.getElementById("transaction_date");

    if (transactionType && categorySelect) {
        const categories = Array.from(categorySelect.options).map(
            (option) => ({
                value: option.value,
                text: option.textContent,
                type: option.dataset.type
            })
        );

        function filterCategories() {
            const selectedType = transactionType.value;
            const currentCategory = categorySelect.value;

            categorySelect.innerHTML = "";

            const validCategories = categories.filter((category) => {
                return (
                    category.type === selectedType ||
                    category.type === "Both"
                );
            });

            validCategories.forEach((category) => {
                const option = document.createElement("option");

                option.value = category.value;
                option.textContent = category.text;

                if (category.value === currentCategory) {
                    option.selected = true;
                }

                categorySelect.appendChild(option);
            });

            // If the previously selected category is not valid for the
            // new transaction type, select the first valid category.
            if (
                !validCategories.some(
                    (category) => category.value === currentCategory
                ) &&
                validCategories.length > 0
            ) {
                categorySelect.value = validCategories[0].value;
            }
        }

        transactionType.addEventListener(
            "change",
            filterCategories
        );

        filterCategories();
    }

    function setDefaultTransactionDate() {
        if (
            !transactionDate ||
            transactionDate.value
        ) {
            return;
        }

        const today = new Date();

        const localDate = new Date(
            today.getTime() -
            today.getTimezoneOffset() * 60000
        )
            .toISOString()
            .split("T")[0];

        transactionDate.value = localDate;
    }

    setDefaultTransactionDate();
});
