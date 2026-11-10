
// ---------------------------------------
// COMBINED EXPERIMENT COMPARISON HISTORY
// ---------------------------------------

const combinedExperimentHistory = [];


// ---------------------------------------
// UPDATE SLIDER VALUES
// ---------------------------------------

function updateValue(input, outputId) {
    const output = document.getElementById(outputId);

    if (output) {
        output.textContent = input.value;
    }
}


// ---------------------------------------
// GET FORM VALUES
// ---------------------------------------

function getFormData(form) {
    const data = {};
    const formData = new FormData(form);

    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    const numericFields = [
        "humidity",
        "temperature",
        "biological_temperature",
        "radiation",
        "vacuum",
        "space_temperature"
    ];

    numericFields.forEach(field => {
        if (data[field] !== undefined) {
            data[field] = Number(data[field]);
        }
    });

    data.microgravity =
        form.querySelector('[name="microgravity"]')?.checked || false;

    return data;
}


// ---------------------------------------
// DISPLAY ERRORS
// ---------------------------------------

function showError(element, message) {
    if (!element) {
        console.error(message);
        return;
    }

    const error = document.createElement("p");
    error.className = "result-error";
    error.textContent = message;

    element.replaceChildren(error);
}


// ---------------------------------------
// DISPLAY EXPERIMENT RESULTS
// ---------------------------------------

function displayResult(mode, result, inputData) {
    const output = document.getElementById(mode + "-result");

    if (!output) {
        console.error("Result container not found:", mode);
        return;
    }

    if (mode === "cryptobiosis") {
        output.innerHTML = `
            <h3>Cryptobiosis Results</h3>

            <div class="stress-number">
                ${result.stress_index}
            </div>

            <p><strong>Modelled stress index:</strong> out of 100</p>
            <p>Biological state: ${result.state}</p>
            <p>Dehydration index: ${result.dehydration}%</p>
            <p>Temperature stress: ${result.temperature_stress}%</p>
            <p>Dehydration contribution: ${result.dehydration_contribution}</p>
            <p>Temperature contribution: ${result.temperature_contribution}</p>
        `;
    }

    else if (mode === "space") {
        output.innerHTML = `
            <h3>Space Conditions Results</h3>

            <div class="stress-number">
                ${result.stress_index}
            </div>

            <p><strong>Modelled stress index:</strong> out of 100</p>
            <p>Radiation index: ${result.radiation_index}%</p>
            <p>Vacuum index: ${result.vacuum_index}%</p>
            <p>Temperature index: ${result.temperature_index}%</p>
            <p>Microgravity included: ${result.microgravity ? "Yes" : "No"}</p>
        `;
    }

    else if (mode === "combined") {
        const crypto = result.cryptobiosis;
        const space = result.space;

        output.innerHTML = `
            <h3>Combined Experiment Results</h3>

            <div class="stress-number">
                ${result.combined_stress_index}
            </div>

            <p><strong>Combined modelled stress index:</strong> out of 100</p>

            <h4>Cryptobiosis Results</h4>
            <p>Cryptobiosis stress index: ${crypto.stress_index}</p>
            <p>Biological state: ${crypto.state}</p>
            <p>Dehydration index: ${crypto.dehydration}%</p>
            <p>Temperature stress: ${crypto.temperature_stress}%</p>

            <h4>Space Conditions Results</h4>
            <p>Space stress index: ${space.stress_index}</p>
            <p>Radiation index: ${space.radiation_index}%</p>
            <p>Vacuum index: ${space.vacuum_index}%</p>
            <p>Temperature index: ${space.temperature_index}%</p>
            <p>Microgravity included: ${space.microgravity ? "Yes" : "No"}</p>

            <h4>Combined Model Explanation</h4>
            <p>
                The combined index uses a 45% cryptobiosis and
                55% space-condition weighting.
            </p>

            <p>
                This is a modelled stress index, not a measured
                survival probability or proof of actual survival.
            </p>
        `;

        saveCombinedExperiment(inputData, result);
    }
}


// ---------------------------------------
// SAVE COMBINED EXPERIMENT
// ---------------------------------------

function saveCombinedExperiment(inputData, result) {
    const crypto = result.cryptobiosis;
    const space = result.space;

    const experiment = {
        run: combinedExperimentHistory.length + 1,

        humidity: inputData.humidity,
        biologicalTemperature: inputData.biological_temperature,
        state: inputData.state,

        radiation: inputData.radiation,
        vacuum: inputData.vacuum,
        spaceTemperature: inputData.space_temperature,
        microgravity: inputData.microgravity,

        cryptoStress: crypto.stress_index,
        spaceStress: space.stress_index,
        combinedStress: result.combined_stress_index
    };

    combinedExperimentHistory.push(experiment);

    renderComparisonHistory();
}


// ---------------------------------------
// CREATE COMPARISON HISTORY SECTION
// ---------------------------------------

function renderComparisonHistory() {
    const combinedOutput = document.getElementById("combined-result");

    if (!combinedOutput) {
        return;
    }

    let section = document.getElementById("combined-comparison");

    if (!section) {
        section = document.createElement("section");
        section.id = "combined-comparison";
        section.className = "comparison-section";

        combinedOutput.insertAdjacentElement("afterend", section);
    }

    section.replaceChildren();

    const heading = document.createElement("h3");
    heading.textContent = "Experiment Comparison";

    const description = document.createElement("p");
    description.textContent =
        "Compare the results of different combined experiments.";

    const tableWrapper = document.createElement("div");
    tableWrapper.className = "comparison-table-wrapper";

    const table = document.createElement("table");
    table.className = "comparison-table";

    const headers = [
        "Run",
        "Biological State",
        "Humidity (%)",
        "Biological Temp (°C)",
        "Radiation",
        "Vacuum",
        "Space Temp (°C)",
        "Microgravity",
        "Cryptobiosis Stress",
        "Space Stress",
        "Combined Stress"
    ];

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    headers.forEach(header => {
        const th = document.createElement("th");
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);

    const tbody = document.createElement("tbody");

    combinedExperimentHistory.forEach(experiment => {
        const row = document.createElement("tr");

        const values = [
            experiment.run,
            experiment.state,
            experiment.humidity,
            experiment.biologicalTemperature,
            experiment.radiation,
            experiment.vacuum,
            experiment.spaceTemperature,
            experiment.microgravity ? "Yes" : "No",
            experiment.cryptoStress,
            experiment.spaceStress,
            experiment.combinedStress
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value ?? "N/A";
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    tableWrapper.appendChild(table);

    const note = document.createElement("p");
    note.className = "comparison-note";
    note.textContent =
        "Lower or higher modelled stress values should be interpreted " +
        "according to the simulation assumptions. They do not represent " +
        "experimentally measured survival rates.";

    const clearButton = document.createElement("button");
    clearButton.type = "button";
    clearButton.className = "run-button";
    clearButton.textContent = "Clear Comparison History";

    clearButton.addEventListener("click", function() {
        combinedExperimentHistory.length = 0;
        section.remove();
    });

    section.appendChild(heading);
    section.appendChild(description);
    section.appendChild(tableWrapper);
    section.appendChild(note);
    section.appendChild(clearButton);
}


// ---------------------------------------
// CONNECT SIMULATION FORMS TO FLASK
// Only forms with data-mode are handled.
// The radiation analysis form is submitted
// normally to its own Flask route.
// ---------------------------------------

document.querySelectorAll(".experiment-form[data-mode]").forEach(form => {

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const mode = form.dataset.mode;
        const output = document.getElementById(mode + "-result");
        const button = form.querySelector("button");

        if (!output || !button) {
            console.error("Simulation result area or button is missing.");
            return;
        }

        button.disabled = true;
        button.textContent = "Running experiment...";

        try {
            const data = getFormData(form);
            data.mode = mode;

            const csrfElement = document.querySelector(
                'meta[name="csrf-token"]'
            );

            const csrfToken = csrfElement ? csrfElement.content : "";

            const response = await fetch("/api/lab/simulate", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },

                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.error || "Experiment failed."
                );
            }

            displayResult(mode, result, data);

        } catch (error) {
            showError(output, error.message);

        } finally {
            button.disabled = false;

            if (mode === "cryptobiosis") {
                button.textContent = "Run Cryptobiosis Experiment";
            }

            else if (mode === "space") {
                button.textContent = "Run Space Experiment";
            }

            else if (mode === "combined") {
                button.textContent = "Run Combined Experiment";
            }
        }
    });

});
/* =================================
   INTERACTIVE TARDIGRADE VISUAL
================================= */

document.addEventListener("DOMContentLoaded", function () {

    const tardigrade = document.getElementById("tardigrade");
    const tunShape = document.getElementById("tun-shape");
    const scene = document.getElementById("tardigrade-scene");

    const visualState = document.getElementById("visual-state");
    const visualCondition = document.getElementById("visual-condition");
    const visualMode = document.getElementById("visual-mode");
    const sceneCaption = document.getElementById("scene-caption");

    if (!tardigrade || !tunShape || !scene) {
        return;
    }

    function updateLaboratoryVisual(form) {

        const mode = form.dataset.mode;

        const getValue = function (name) {
            const field = form.querySelector(`[name="${name}"]`);
            return field ? field.value : null;
        };

        const humidity = Number(getValue("humidity") || 100);

        const radiation = Number(getValue("radiation") || 0);

        const vacuum = Number(getValue("vacuum") || 0);

        const state = (getValue("state") || "active").toLowerCase();

        const isTun = [
            "tun",
            "dormant",
            "cryptobiotic"
        ].includes(state);

        tardigrade.classList.toggle("is-hidden", isTun);
        tunShape.classList.toggle("is-visible", isTun);

        visualState.textContent = isTun
            ? "State: Tun / Cryptobiotic"
            : "State: Active";

        visualMode.textContent = "Mode: " + mode;

        let stressed = false;

        if (mode === "cryptobiosis" || mode === "combined") {
            if (humidity < 30) {
                stressed = true;
            }
        }

        if (mode === "space" || mode === "combined") {
            if (radiation > 5 || vacuum > 50) {
                stressed = true;
            }
        }

        scene.classList.toggle("environment-stress", stressed);

        visualCondition.textContent = stressed
            ? "Environment: High stress conditions"
            : "Environment: Relatively mild conditions";

        if (isTun) {
            sceneCaption.textContent =
                "The tardigrade is represented in its contracted tun form. This visual is illustrative.";
        } else if (stressed) {
            sceneCaption.textContent =
                "Environmental stress conditions are elevated. Observe the selected simulation results for the model's calculated response.";
        } else {
            sceneCaption.textContent =
                "The tardigrade is shown in its active form under the selected conditions.";
        }
    }

    document.querySelectorAll(".experiment-form[data-mode]").forEach(form => {

        form.addEventListener("input", function () {
            updateLaboratoryVisual(form);
        });

        form.addEventListener("change", function () {
            updateLaboratoryVisual(form);
        });

    });

    const initialForm = document.querySelector(
        '.experiment-form[data-mode="cryptobiosis"]'
    ) || document.querySelector(".experiment-form[data-mode]");

    if (initialForm) {
        updateLaboratoryVisual(initialForm);
    }

});