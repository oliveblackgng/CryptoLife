
/* =====================================
   CRYPTOLIFE - RESEARCH LIBRARY
===================================== */

// CSRF token for secure POST requests

const csrfToken = document.querySelector(
    'meta[name="csrf-token"]'
)?.content;


// Escape API text before inserting it into HTML

function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);

}


// =====================================
// SEARCH SCIENTIFIC PUBLICATIONS
// =====================================

const searchForm = document.getElementById("search-form");

if (searchForm) {

    searchForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const query = document.getElementById(
            "search-query"
        ).value.trim();

        const year = document.getElementById(
            "year-filter"
        ).value;

        const openAccess = document.getElementById(
            "oa-filter"
        ).checked;

        const resultsContainer = document.getElementById(
            "paper-results"
        );

        const status = document.getElementById(
            "search-status"
        );

        const button = document.getElementById(
            "search-button"
        );

        if (!query) {
            status.textContent = "Please enter a search term.";
            return;
        }

        resultsContainer.innerHTML = "";

        status.textContent =
            "Searching scientific publications...";

        button.disabled = true;

        try {

            const params = new URLSearchParams({
                q: query
            });

            if (year) {
                params.append("year", year);
            }

            if (openAccess) {
                params.append("open_access", "true");
            }

            const response = await fetch(
                `/api/research/search?${params.toString()}`
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Search failed."
                );
            }

            status.textContent =
                `${data.count} research results found`;

            if (!data.results.length) {

                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <h3>No papers found.</h3>
                        <p>Try another search term.</p>
                    </div>
                `;

                return;
            }


            // Display each paper

            data.results.forEach(paper => {

                const card = document.createElement("article");

                card.className = "paper-card";

                const authors = paper.authors.length
                    ? paper.authors.join(", ")
                    : "Author information unavailable";

                const abstract = paper.abstract
                    ? paper.abstract
                    : "Abstract unavailable for this publication.";

                const publicationLink = paper.paper_url
                    ? `
                        <a href="${escapeHTML(paper.paper_url)}"
                           target="_blank"
                           rel="noopener noreferrer">
                           View publication ↗
                        </a>
                    `
                    : "";

                const pdfLink = paper.pdf_url
                    ? `
                        <a href="${escapeHTML(paper.pdf_url)}"
                           target="_blank"
                           rel="noopener noreferrer">
                           Open-access PDF ↗
                        </a>
                    `
                    : "";

                card.innerHTML = `

                    <div class="paper-top">

                        <span class="source-tag">
                            OpenAlex
                        </span>

                        <span>
                            ${escapeHTML(
                                paper.year || "Year unavailable"
                            )}
                        </span>

                    </div>


                    <h2>
                        ${escapeHTML(paper.title)}
                    </h2>


                    <p class="paper-authors">
                        ${escapeHTML(authors)}
                    </p>


                    <p class="journal-name">
                        ${escapeHTML(
                            paper.journal || "Journal unavailable"
                        )}
                    </p>


                    <p class="paper-abstract">
                        ${escapeHTML(abstract)}
                    </p>


                    <div class="paper-links">

                        ${publicationLink}

                        ${pdfLink}

                    </div>


                    <div class="paper-bottom">

                        <span class="access-tag">
                            ${paper.is_open_access
                                ? "Open Access"
                                : "Access may be restricted"}
                        </span>

                        <button class="save-button">
                            Save Paper
                        </button>

                    </div>

                `;


                // Save button event

                const saveButton = card.querySelector(
                    ".save-button"
                );

                saveButton.addEventListener("click", function() {

                    savePaper(paper, saveButton);

                });


                resultsContainer.appendChild(card);

            });

        }

        catch (error) {

            status.textContent = error.message;

            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>Search unavailable</h3>
                    <p>${escapeHTML(error.message)}</p>
                    <p>Please try again.</p>
                </div>
            `;

        }

        finally {

            button.disabled = false;

        }

    });

}


// =====================================
// SAVE PAPER TO PERSONAL LIBRARY
// =====================================


async function savePaper(paper, button) {

    button.disabled = true;
    button.textContent = "Saving...";

    try {

        const response = await fetch("/api/research/save", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },

            body: JSON.stringify(paper)
        });

        // Read the response as text first
        const responseText = await response.text();

        let data;

        try {
            data = JSON.parse(responseText);
        } catch (error) {
            console.error("Server returned HTML instead of JSON:");
            console.error(responseText);

            throw new Error(
                `Server error (${response.status}). Check the Flask terminal for details.`
            );
        }

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to save paper."
            );
        }

        button.textContent = "Saved ✓";

        alert("Paper saved successfully!");

    } catch (error) {

        console.error("Save error:", error);

        button.textContent = "Try Again";

        alert(error.message);

    } finally {

        button.disabled = false;

    }
}



// =====================================
// REMOVE SAVED PAPER
// =====================================

async function removePaper(paperId, button) {

    const confirmed = confirm(
        "Remove this paper from your research library?"
    );

    if (!confirmed) {
        return;
    }

    button.disabled = true;

    try {

        const response = await fetch(
            `/api/research/unsave/${paperId}`,
            {

                method: "POST",

                headers: {
                    "X-CSRFToken": csrfToken
                }

            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.error || "Unable to remove paper."
            );

        }

        button.closest(".paper-card").remove();

    }

    catch (error) {

        alert(error.message);

        button.disabled = false;

    }

}
// Handle remove paper buttons

document.addEventListener("click", function(event) {

    const button = event.target.closest(".remove-button");

    if (!button) {
        return;
    }

    const paperId = button.dataset.paperId;

    removePaper(paperId, button);

});