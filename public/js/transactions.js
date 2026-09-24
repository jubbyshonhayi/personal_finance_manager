const allCategoryOptions = categorySelect
    ? Array.from(categorySelect.options).map((option) =>
        option.cloneNode(true)
    )
    : [];

function filterCategories() {
    if (!transactionType || !categorySelect) {
        return;
    }

    const selectedType = transactionType.value;
    const currentCategory = categorySelect.value;

    // Keep only categories that match the selected transaction type.
    const matchingOptions = allCategoryOptions.filter((option) => {
        const categoryType = option.dataset.type;

        return (
            option.value === "" ||
            categoryType === selectedType ||
            categoryType === "Both"
        );
    });

    // Rebuild the select instead of hiding options, which is more reliable
    // across browsers and mobile devices.
    categorySelect.replaceChildren();

    for (const option of matchingOptions) {
        categorySelect.appendChild(option.cloneNode(true));
    }

    const currentCategoryStillExists = matchingOptions.some(
        (option) => option.value === currentCategory
    );

    if (currentCategoryStillExists) {
        categorySelect.value = currentCategory;
        return;
    }

    const firstSelectableOption = matchingOptions.find(
        (option) => option.value !== ""
    );

    if (firstSelectableOption) {
        categorySelect.value = firstSelectableOption.value;
    }
}

function setDefaultTransactionDate() {
    if (
        !transactionDate ||
        transactionDate.value
    ) {
        return;
    }

    const today = new Date();

    // Convert the date to the user's local date before formatting it.
    const localDate = new Date(
        today.getTime() -
        today.getTimezoneOffset() * 60000
    )
        .toISOString()
        .split("T")[0];

    transactionDate.value = localDate;
}

if (transactionType && categorySelect) {
    transactionType.addEventListener(
        "change",
        filterCategories
    );

    filterCategories();
}

setDefaultTransactionDate();
