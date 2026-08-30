document.addEventListener("DOMContentLoaded", function () {

    "use strict";


    // =====================================================
    // ELEMENTS
    // =====================================================

    const page = document.getElementById("billingPage");

    const form = document.getElementById("billingForm");

    const patientSelect =
        document.getElementById("patient");

    const doctorSelect =
        document.getElementById("doctor");

    const appointmentSelect =
        document.getElementById("appointment");

    const appointmentHelp =
        document.getElementById("appointmentHelp");

    const consultationInput =
        document.getElementById("consultation_fee");

    const medicineChargesInput =
        document.getElementById("medicine_charges");

    const labInput =
        document.getElementById("lab_charges");

    const roomInput =
        document.getElementById("room_charges");

    const amountPaidInput =
        document.getElementById("amount_paid");

    const paymentMethod =
        document.getElementById("payment_method");

    const medicineRows =
        document.getElementById("medicineRows");

    const medicineEmpty =
        document.getElementById("medicineEmpty");

    const addMedicineBtn =
        document.getElementById("addMedicineBtn");

    const summaryPatient =
        document.getElementById("summaryPatient");

    const summaryConsultation =
        document.getElementById("summaryConsultation");

    const summaryMedicine =
        document.getElementById("summaryMedicine");

    const summaryLab =
        document.getElementById("summaryLab");

    const summaryRoom =
        document.getElementById("summaryRoom");

    const summaryTotal =
        document.getElementById("summaryTotal");

    const summaryPaid =
        document.getElementById("summaryPaid");

    const summaryBalance =
        document.getElementById("summaryBalance");

    const summaryPaymentStatus =
        document.getElementById(
            "summaryPaymentStatus"
        );

    const displayConsultation =
        document.getElementById(
            "displayConsultation"
        );

    const displayMedicine =
        document.getElementById(
            "displayMedicine"
        );

    const displayLab =
        document.getElementById(
            "displayLab"
        );

    const displayRoom =
        document.getElementById(
            "displayRoom"
        );

    const displayTotal =
        document.getElementById(
            "displayTotal"
        );

    const medicineItemsTotal =
        document.getElementById(
            "medicineItemsTotal"
        );

    const paymentStatusMessage =
        document.getElementById(
            "paymentStatusMessage"
        );

    const previousBilling =
        document.getElementById(
            "previousBilling"
        );

    const previousBillingList =
        document.getElementById(
            "previousBillingList"
        );

    const previousBillCount =
        document.getElementById(
            "previousBillCount"
        );


    if (!page || !form) {
        return;
    }


    // =====================================================
    // URLS
    // =====================================================

    const patientUrlTemplate =
        page.dataset.patientUrlTemplate;

    const doctorUrlTemplate =
        page.dataset.doctorUrlTemplate;

    const medicineUrlTemplate =
        page.dataset.medicineUrlTemplate;


    function buildUrl(template, id) {

        return template.replace(
            "/0/",
            `/${id}/`
        );
    }


    // =====================================================
    // MONEY
    // =====================================================

    function money(value) {

        const number =
            Number(value) || 0;

        return (
            "₹" +
            number.toLocaleString(
                "en-IN",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            )
        );
    }


    function numericValue(input) {

        if (!input) {
            return 0;
        }

        const value =
            parseFloat(input.value);

        return Number.isFinite(value)
            ? Math.max(value, 0)
            : 0;
    }


    // =====================================================
    // QUANTITY NORMALIZATION
    // =====================================================

    function normalizeQuantity(input) {

        let value =
            input.value.replace(
                /[^0-9]/g,
                ""
            );

        if (value === "") {

            input.value = "0";

            return;
        }

        value = value.replace(
            /^0+(?=\d)/,
            ""
        );

        input.value = value || "0";
    }


    // =====================================================
    // DOCTOR
    // =====================================================

    doctorSelect.addEventListener(
        "change",
        function () {

            const doctorId =
                this.value;

            consultationInput.value =
                "0.00";

            if (!doctorId) {

                recalculate();

                return;
            }

            const url =
                buildUrl(
                    doctorUrlTemplate,
                    doctorId
                );

            fetch(url)
                .then(response => {

                    if (!response.ok) {
                        throw new Error(
                            "Unable to load doctor."
                        );
                    }

                    return response.json();
                })
                .then(data => {

                    consultationInput.value =
                        Number(
                            data.consultation_fee || 0
                        ).toFixed(2);

                    recalculate();
                })
                .catch(error => {

                    console.error(error);

                    consultationInput.value =
                        "0.00";

                    recalculate();
                });
        }
    );


    // =====================================================
    // PATIENT
    // =====================================================

    patientSelect.addEventListener(
        "change",
        function () {

            const patientId =
                this.value;

            resetAppointments();

            clearPreviousBilling();

            const selectedOption =
                this.options[
                    this.selectedIndex
                ];

            if (!patientId) {

                summaryPatient.textContent =
                    "Not Selected";

                return;
            }

            summaryPatient.textContent =
                selectedOption.textContent.trim();

            appointmentHelp.textContent =
                "Loading appointments...";

            const url =
                buildUrl(
                    patientUrlTemplate,
                    patientId
                );

            fetch(url)
                .then(response => {

                    if (!response.ok) {
                        throw new Error(
                            "Unable to load patient data."
                        );
                    }

                    return response.json();
                })
                .then(data => {

                    loadAppointments(
                        data.appointments || []
                    );

                    loadPreviousBills(
                        data.bills || []
                    );
                })
                .catch(error => {

                    console.error(error);

                    appointmentHelp.textContent =
                        "Unable to load appointments.";

                });
        }
    );


    // =====================================================
    // LOAD APPOINTMENTS
    // =====================================================

    function loadAppointments(
        appointments
    ) {

        resetAppointments();

        if (!appointments.length) {

            appointmentHelp.textContent =
                "No available appointments for this patient.";

            return;
        }

        appointments.forEach(
            appointment => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    appointment.id;

                option.dataset.doctorId =
                    appointment.doctor_id;

                option.textContent =
                    `${appointment.date} ${appointment.time} - Dr. ${appointment.doctor_name}`;

                appointmentSelect.appendChild(
                    option
                );
            }
        );

        appointmentHelp.textContent =
            `${appointments.length} appointment(s) available.`;
    }


    function resetAppointments() {

        appointmentSelect.innerHTML = "";

        const option =
            document.createElement(
                "option"
            );

        option.value = "";

        option.textContent =
            "Select Appointment";

        appointmentSelect.appendChild(
            option
        );

        appointmentHelp.textContent =
            "Select a patient first";
    }


    // =====================================================
    // APPOINTMENT → DOCTOR
    // =====================================================

    appointmentSelect.addEventListener(
        "change",
        function () {

            const selected =
                this.options[
                    this.selectedIndex
                ];

            const doctorId =
                selected.dataset.doctorId;

            if (!doctorId) {
                return;
            }

            doctorSelect.value =
                doctorId;

            doctorSelect.dispatchEvent(
                new Event("change")
            );
        }
    );


    // =====================================================
    // PREVIOUS BILLING
    // =====================================================

    function loadPreviousBills(
        bills
    ) {

        previousBillingList.innerHTML = "";

        if (!bills.length) {

            previousBilling.hidden = false;

            previousBillCount.textContent =
                "No previous bills";

            previousBillingList.innerHTML = `
                <div class="previous-billing-empty">
                    No previous billing records found for this patient.
                </div>
            `;

            return;
        }

        previousBilling.hidden = false;

        previousBillCount.textContent =
            `${bills.length} recent bill${bills.length === 1 ? "" : "s"}`;


        bills.forEach(
            bill => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "previous-bill-item";


                item.innerHTML = `

                    <div class="previous-bill-info">

                        <strong>
                            ${escapeHtml(
                                bill.bill_number
                            )}
                        </strong>

                        <small>
                            ${escapeHtml(
                                bill.date
                            )}
                            ·
                            Dr. ${escapeHtml(
                                bill.doctor
                            )}
                        </small>

                    </div>


                    <div class="previous-bill-amount">

                        <strong>
                            ${money(
                                bill.total
                            )}
                        </strong>

                        <small>
                            ${escapeHtml(
                                bill.status
                            )}
                        </small>

                    </div>


                    <a
                        href="/billing/detail/${bill.id}/"
                        class="previous-bill-link"
                    >
                        View
                    </a>

                `;

                previousBillingList.appendChild(
                    item
                );
            }
        );
    }


    function clearPreviousBilling() {

        previousBilling.hidden = true;

        previousBillingList.innerHTML = "";

        previousBillCount.textContent =
            "0 bills";
    }


    function escapeHtml(value) {

        const div =
            document.createElement(
                "div"
            );

        div.textContent =
            value ?? "";

        return div.innerHTML;
    }


    // =====================================================
    // ADD MEDICINE
    // =====================================================

    addMedicineBtn.addEventListener(
        "click",
        function () {

            addMedicineRow();

        }
    );


    function addMedicineRow() {

        medicineEmpty.style.display =
            "none";


        const row =
            document.createElement(
                "div"
            );

        row.className =
            "medicine-row";


        row.innerHTML = `

            <div class="medicine-row-field medicine-select-field">

                <label>
                    Medicine
                </label>

                <select
                    name="medicine_id[]"
                    class="medicine-select"
                    required
                >

                    <option value="">
                        Select Medicine
                    </option>

                    {% for medicine in medicines %}

                        <option
                            value="{{ medicine.id }}"
                            data-price="{{ medicine.price }}"
                            data-stock="{{ medicine.quantity }}"
                        >

                            {{ medicine.medicine_name }}
                            —
                            ₹{{ medicine.price }}
                            —
                            Stock: {{ medicine.quantity }}

                        </option>

                    {% endfor %}

                </select>

                <small class="medicine-stock">
                    Select medicine
                </small>

            </div>


            <div class="medicine-row-field">

                <label>
                    Unit Price
                </label>

                <div class="amount-input">

                    <span>₹</span>

                    <input
                        type="number"
                        class="medicine-price"
                        value="0.00"
                        readonly
                    >

                </div>

            </div>


            <div class="medicine-row-field">

                <label>
                    Quantity
                </label>

                <input
                    type="number"
                    name="medicine_qty[]"
                    class="medicine-qty"
                    value="1"
                    min="1"
                    step="1"
                >

                <small class="quantity-help">
                    Maximum: 0
                </small>

            </div>


            <div class="medicine-row-field">

                <label>
                    Total
                </label>

                <div class="amount-input">

                    <span>₹</span>

                    <input
                        type="number"
                        class="medicine-total"
                        value="0.00"
                        readonly
                    >

                </div>

            </div>


            <button
                type="button"
                class="remove-medicine-btn"
                title="Remove medicine"
            >
                ×
            </button>

        `;


        medicineRows.appendChild(
            row
        );


        const select =
            row.querySelector(
                ".medicine-select"
            );

        const quantity =
            row.querySelector(
                ".medicine-qty"
            );

        const removeButton =
            row.querySelector(
                ".remove-medicine-btn"
            );


        select.addEventListener(
            "change",
            function () {

                updateMedicineRow(
                    row
                );

                refreshMedicineOptions();
            }
        );


        quantity.addEventListener(
            "focus",
            function () {

                this.select();
            }
        );


        quantity.addEventListener(
            "input",
            function () {

                normalizeQuantity(
                    this
                );

                updateMedicineRow(
                    row
                );
            }
        );


        quantity.addEventListener(
            "blur",
            function () {

                if (
                    !this.value ||
                    Number(this.value) < 1
                ) {

                    this.value = "1";
                }

                updateMedicineRow(
                    row
                );
            }
        );


        removeButton.addEventListener(
            "click",
            function () {

                row.remove();

                refreshMedicineOptions();

                calculateMedicineTotal();

                updateEmptyMedicineState();
            }
        );


        refreshMedicineOptions();

    }


    // =====================================================
    // MEDICINE ROW CALCULATION
    // =====================================================

    function updateMedicineRow(
        row
    ) {

        const select =
            row.querySelector(
                ".medicine-select"
            );

        const priceInput =
            row.querySelector(
                ".medicine-price"
            );

        const quantityInput =
            row.querySelector(
                ".medicine-qty"
            );

        const totalInput =
            row.querySelector(
                ".medicine-total"
            );

        const stockText =
            row.querySelector(
                ".medicine-stock"
            );

        const quantityHelp =
            row.querySelector(
                ".quantity-help"
            );


        const option =
            select.options[
                select.selectedIndex
            ];


        if (
            !select.value ||
            !option
        ) {

            priceInput.value =
                "0.00";

            totalInput.value =
                "0.00";

            stockText.textContent =
                "Select medicine";

            quantityHelp.textContent =
                "Maximum: 0";

            calculateMedicineTotal();

            return;
        }


        const price =
            Number(
                option.dataset.price || 0
            );

        const stock =
            Number(
                option.dataset.stock || 0
            );


        let quantity =
            parseInt(
                quantityInput.value || 1,
                10
            );


        if (!Number.isFinite(quantity)) {

            quantity = 1;
        }


        if (quantity < 1) {

            quantity = 1;
        }


        if (quantity > stock) {

            quantity = stock;
        }


        quantityInput.value =
            quantity;


        priceInput.value =
            price.toFixed(2);


        const total =
            price * quantity;


        totalInput.value =
            total.toFixed(2);


        stockText.textContent =
            `Available stock: ${stock}`;


        quantityHelp.textContent =
            `Maximum: ${stock}`;


        calculateMedicineTotal();
    }


    // =====================================================
    // DUPLICATE MEDICINE PREVENTION
    // =====================================================

    function refreshMedicineOptions() {

        const selectedIds =
            new Set();


        document
            .querySelectorAll(
                ".medicine-select"
            )
            .forEach(select => {

                if (select.value) {

                    selectedIds.add(
                        select.value
                    );
                }
            });


        document
            .querySelectorAll(
                ".medicine-select"
            )
            .forEach(select => {

                const currentValue =
                    select.value;


                Array.from(
                    select.options
                ).forEach(option => {

                    if (!option.value) {
                        return;
                    }

                    option.disabled =
                        selectedIds.has(
                            option.value
                        )
                        &&
                        option.value !==
                            currentValue;
                });
            });
    }


    // =====================================================
    // MEDICINE TOTAL
    // =====================================================

    function calculateMedicineTotal() {

        let total = 0;


        document
            .querySelectorAll(
                ".medicine-total"
            )
            .forEach(input => {

                total +=
                    Number(input.value) || 0;

            });


        medicineChargesInput.value =
            total.toFixed(2);


        medicineItemsTotal.textContent =
            money(total);


        displayMedicine.textContent =
            money(total);


        summaryMedicine.textContent =
            money(total);


        recalculate();
    }


    function updateEmptyMedicineState() {

        const rows =
            document.querySelectorAll(
                ".medicine-row"
            );


        medicineEmpty.style.display =
            rows.length
                ? "none"
                : "block";
    }


    // =====================================================
    // CHARGE INPUTS
    // =====================================================

    [
        consultationInput,
        labInput,
        roomInput,
        amountPaidInput
    ].forEach(input => {

        input.addEventListener(
            "focus",
            function () {

                this.select();
            }
        );


        input.addEventListener(
            "input",
            function () {

                if (
                    this.value !== ""
                    &&
                    Number(this.value) < 0
                ) {

                    this.value = "0";
                }

                recalculate();
            }
        );

    });


    // =====================================================
    // PAYMENT STATUS
    // =====================================================

    document
        .querySelectorAll(
            ".payment-radio"
        )
        .forEach(radio => {

            radio.addEventListener(
                "change",
                function () {

                    updatePaymentState();

                }
            );

        });


    function getPaymentStatus() {

        const checked =
            document.querySelector(
                'input[name="payment_status"]:checked'
            );

        return checked
            ? checked.value
            : "Pending";
    }


    function updatePaymentState() {

        const status =
            getPaymentStatus();


        const total =
            calculateTotal();


        if (status === "Paid") {

            amountPaidInput.value =
                total.toFixed(2);

            amountPaidInput.readOnly =
                true;

        }

        else if (status === "Pending") {

            amountPaidInput.value =
                "0.00";

            amountPaidInput.readOnly =
                true;

        }

        else if (status === "Partial") {

            amountPaidInput.readOnly =
                false;

        }


        updatePaymentMessage(
            status
        );


        recalculate();
    }


    function updatePaymentMessage(
        status
    ) {

        const messages = {

            Paid:
                "Payment is fully received.",

            Pending:
                "Payment is currently pending.",

            Partial:
                "Partial payment is being recorded."

        };


        paymentStatusMessage.innerHTML =
            messages[status] ||
            "Payment status selected.";


        summaryPaymentStatus.textContent =
            status;


        summaryPaymentStatus.className =
            "status-" +
            status.toLowerCase();

    }


    // =====================================================
    // TOTAL
    // =====================================================

    function calculateTotal() {

        const consultation =
            numericValue(
                consultationInput
            );

        const medicine =
            numericValue(
                medicineChargesInput
            );

        const lab =
            numericValue(
                labInput
            );

        const room =
            numericValue(
                roomInput
            );


        return (
            consultation
            + medicine
            + lab
            + room
        );
    }


    function recalculate() {

        const consultation =
            numericValue(
                consultationInput
            );

        const medicine =
            numericValue(
                medicineChargesInput
            );

        const lab =
            numericValue(
                labInput
            );

        const room =
            numericValue(
                roomInput
            );

        const total =
            consultation
            + medicine
            + lab
            + room;


        let paid =
            numericValue(
                amountPaidInput
            );


        const status =
            getPaymentStatus();


        if (status === "Paid") {

            paid = total;

            amountPaidInput.value =
                total.toFixed(2);

        }

        else if (status === "Pending") {

            paid = 0;

            amountPaidInput.value =
                "0.00";

        }

        else if (status === "Partial") {

            if (paid > total) {

                paid = total;

                amountPaidInput.value =
                    total.toFixed(2);
            }
        }


        const balance =
            Math.max(
                total - paid,
                0
            );


        // ---------------------------------------------
        // CALCULATION STRIP
        // ---------------------------------------------

        displayConsultation.textContent =
            money(consultation);

        displayMedicine.textContent =
            money(medicine);

        displayLab.textContent =
            money(lab);

        displayRoom.textContent =
            money(room);

        displayTotal.textContent =
            money(total);


        // ---------------------------------------------
        // SUMMARY
        // ---------------------------------------------

        summaryConsultation.textContent =
            money(consultation);

        summaryMedicine.textContent =
            money(medicine);

        summaryLab.textContent =
            money(lab);

        summaryRoom.textContent =
            money(room);

        summaryTotal.textContent =
            money(total);

        summaryPaid.textContent =
            money(paid);

        summaryBalance.textContent =
            money(balance);


        updatePaymentMessage(
            status
        );
    }


    // =====================================================
    // FORM VALIDATION
    // =====================================================

    form.addEventListener(
        "submit",
        function (event) {

            const total =
                calculateTotal();


            if (!patientSelect.value) {

                event.preventDefault();

                alert(
                    "Please select a patient."
                );

                patientSelect.focus();

                return;
            }


            if (!doctorSelect.value) {

                event.preventDefault();

                alert(
                    "Please select a doctor."
                );

                doctorSelect.focus();

                return;
            }


            if (total <= 0) {

                event.preventDefault();

                alert(
                    "Bill amount must be greater than zero."
                );

                return;
            }


            const status =
                getPaymentStatus();


            const paid =
                numericValue(
                    amountPaidInput
                );


            if (status === "Partial") {

                if (
                    paid <= 0
                    ||
                    paid >= total
                ) {

                    event.preventDefault();

                    alert(
                        "For Partial payment, Amount Paid must be greater than 0 and less than the total amount."
                    );

                    amountPaidInput.focus();

                    return;
                }
            }


            if (
                paid > total
                &&
                status !== "Paid"
            ) {

                event.preventDefault();

                alert(
                    "Amount paid cannot be greater than the total amount."
                );

                amountPaidInput.focus();

                return;
            }


            // =========================================
            // DISABLE SUBMIT TO PREVENT DOUBLE BILL
            // =========================================

            const button =
                document.getElementById(
                    "generateBillBtn"
                );

            if (button) {

                button.disabled = true;

                button.innerHTML = `
                    <span class="generate-icon">
                        ✓
                    </span>
                    Generating Bill...
                `;
            }

        }
    );


    // =====================================================
    // INITIAL STATE
    // =====================================================

    medicineEmpty.style.display =
        "block";

    updatePaymentState();

    recalculate();

});