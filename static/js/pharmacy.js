document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       LOW STOCK WARNING
    ===================================================== */

    const quantityInput = document.getElementById("medicineQuantity");
    const stockWarning = document.getElementById("stockWarning");

    function checkStock() {

        if (!quantityInput || !stockWarning) {
            return;
        }

        const quantity = parseInt(quantityInput.value || "0");

        if (quantity < 10) {
            stockWarning.style.display = "block";
        } else {
            stockWarning.style.display = "none";
        }
    }

    if (quantityInput) {

        checkStock();

        quantityInput.addEventListener(
            "input",
            checkStock
        );
    }


    /* =====================================================
       BILLING
    ===================================================== */

    const billingItems = document.getElementById("billingItems");
    const addMedicineBtn = document.getElementById("addMedicineBtn");
    const grandTotal = document.getElementById("grandTotal");
    const summaryItems = document.getElementById("summaryItems");


    function updateBilling() {

        if (!billingItems) {
            return;
        }

        let total = 0;

        const items =
            billingItems.querySelectorAll(".billing-item");

        summaryItems.innerHTML = "";


        items.forEach(function (item) {

            const select =
                item.querySelector(".medicine-select");

            const quantityInput =
                item.querySelector(".billing-qty");

            const itemTotal =
                item.querySelector(".item-total");


            if (!select || !quantityInput) {
                return;
            }


            const selectedOption =
                select.options[select.selectedIndex];


            if (
                !selectedOption ||
                !selectedOption.value
            ) {

                itemTotal.textContent = "₹0.00";

                return;
            }


            const price =
                parseFloat(
                    selectedOption.dataset.price || "0"
                );

            const stock =
                parseInt(
                    selectedOption.dataset.stock || "0"
                );

            let quantity =
                parseInt(
                    quantityInput.value || "0"
                );


            if (quantity < 1) {
                quantity = 1;
                quantityInput.value = 1;
            }


            /*
             * Don't allow the user to select
             * more than available stock.
             */

            if (quantity > stock) {

                quantity = stock;

                quantityInput.value = stock;

                alert(
                    "Only " +
                    stock +
                    " units of " +
                    selectedOption.text.trim() +
                    " are available."
                );
            }


            const lineTotal =
                price * quantity;


            total += lineTotal;


            itemTotal.textContent =
                "₹" + lineTotal.toFixed(2);


            const summaryRow =
                document.createElement("div");

            summaryRow.className =
                "summary-item";


            const medicineName =
                selectedOption.text
                    .split("—")[0]
                    .trim();


            summaryRow.innerHTML = `
                <span class="summary-item-name">
                    ${medicineName} × ${quantity}
                </span>

                <span class="summary-item-price">
                    ₹${lineTotal.toFixed(2)}
                </span>
            `;


            summaryItems.appendChild(summaryRow);

        });


        if (!summaryItems.children.length) {

            summaryItems.innerHTML = `
                <p class="summary-empty">
                    Select medicines to calculate the bill.
                </p>
            `;
        }


        grandTotal.textContent =
            "₹" + total.toFixed(2);
    }


    /* =====================================================
       ADD MEDICINE ROW
    ===================================================== */

    if (addMedicineBtn) {

        addMedicineBtn.addEventListener(
            "click",
            function () {

                const firstItem =
                    billingItems.querySelector(
                        ".billing-item"
                    );


                if (!firstItem) {
                    return;
                }


                const newItem =
                    firstItem.cloneNode(true);


                newItem
                    .querySelector(".medicine-select")
                    .selectedIndex = 0;


                newItem
                    .querySelector(".billing-qty")
                    .value = 1;


                newItem
                    .querySelector(".item-total")
                    .textContent = "₹0.00";


                billingItems.appendChild(
                    newItem
                );


                updateBilling();
            }
        );
    }


    /* =====================================================
       REMOVE BILLING ITEM
    ===================================================== */

    if (billingItems) {

        billingItems.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.classList.contains(
                        "remove-item"
                    )
                ) {

                    const items =
                        billingItems.querySelectorAll(
                            ".billing-item"
                        );


                    /*
                     * Keep one row.
                     * User can clear its medicine.
                     */

                    if (items.length === 1) {

                        const select =
                            items[0].querySelector(
                                ".medicine-select"
                            );

                        select.selectedIndex = 0;

                        items[0]
                            .querySelector(
                                ".billing-qty"
                            )
                            .value = 1;

                    } else {

                        event.target
                            .closest(".billing-item")
                            .remove();
                    }


                    updateBilling();
                }
            }
        );


        billingItems.addEventListener(
            "change",
            function () {
                updateBilling();
            }
        );


        billingItems.addEventListener(
            "input",
            function () {
                updateBilling();
            }
        );


        updateBilling();
    }

});