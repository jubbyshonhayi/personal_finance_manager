document.addEventListener("DOMContentLoaded", () => {
const transactionType =
document.getElementById("transaction_type");


const categorySelect =
    document.getElementById("category_id");

const transactionDate =
    document.getElementById("transaction_date");

    
function filterCategories() {
    const selectedType = transactionType.value;
    let firstVisibleOption = null;

    for (const option of categorySelect.options) {
        const categoryType = option.dataset.type;

        const shouldShow =
            categoryType === selectedType ||
            categoryType === "Both";

        option.hidden = !shouldShow;

        if (shouldShow && !firstVisibleOption) {
            firstVisibleOption = option;
        }
    }

    const selectedOption =
        categorySelect.options[
            categorySelect.selectedIndex
        ];

    if (
        !selectedOption ||
        selectedOption.hidden
    ) {
        if (firstVisibleOption) {
            categorySelect.value =
                firstVisibleOption.value;
        }
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

    const localDate = new Date(
        today.getTime() -
        today.getTimezoneOffset() * 60000
    )
        .toISOString()
        .split("T")[0];

    transactionDate.value = localDate;
}

if (
    transactionType &&
    categorySelect
) {
    transactionType.addEventListener(
        "change",
        filterCategories
    );

    filterCategories();
}

setDefaultTransactionDate();

});
