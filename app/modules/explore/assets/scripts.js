document.addEventListener('DOMContentLoaded', () => {
    send_query();
});

function send_query() {
    document.getElementById('results').innerHTML = '';
    document.getElementById("results_not_found").style.display = "none";

    const filters = document.querySelectorAll('#filters input, #filters select, #filters [type="radio"]');

    filters.forEach(filter => {
        filter.addEventListener('input', () => {
            const csrfToken = document.getElementById('csrf_token').value;

            const searchCriteria = {
                csrf_token: csrfToken,
                query: document.querySelector('#query').value,
                queryAuthor: document.querySelector('#queryAuthor').value,
                queryTag: document.querySelector('#queryTag').value,
                queryFeatures: document.querySelector('#queryFeatures').value,
                queryModels: document.querySelector('#queryModels').value,
                publication_type: document.querySelector('#publication_type').value,
                sorting: document.querySelector('[name="sorting"]:checked').value,
            };

            fetch('/explore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchCriteria),
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = '';
                    const resultCount = data.length;
                    const resultText = resultCount === 1 ? 'dataset' : 'datasets';
                    document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

                    if (resultCount === 0) {
                        document.getElementById("results_not_found").style.display = "block";
                    } else {
                        document.getElementById("results_not_found").style.display = "none";
                    }

                    data.forEach(dataset => {
                        let card = document.createElement('div');
                        card.className = 'col-12';
                        card.innerHTML = `
                            <div class="card mb-3" style="border: 1px solid #d3d3d3;">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h2 class="h3 mb-1">
                                            <a href="${dataset.url}" class="text-decoration-none text-dark">
                                                ${dataset.title}
                                            </a>
                                        </h2>
                                        <span class="badge bg-secondary">${dataset.publication_type}</span>
                                    </div>
                                    <p class="mb-2 text-secondary fs-4">${dataset.description}</p>
                                    <div class="d-flex flex-wrap mb-2">
                                        ${dataset.tags.map(tag => `<span class="badge me-2 fs-7" style="background-color: lightSkyBlue; color: rgb(0, 119, 255);">${tag}</span>`).join('')}
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-12 col-12 d-flex align-items-center">
                                            <span class="me-2">Rating:</span>
                                            <div id="star-rating-${dataset.id}" class="stars d-flex" style="color: gold;">
                                                ${[1, 2, 3, 4, 5].map(i => `<span data-value="${i}" class="me-1">★</span>`).join('')}
                                            </div>
                                            <span id="average-rating-${dataset.id}" class="ms-2">-</span>
                                            <span class="ms-2">·</span>
                                            <span class="ms-2">Created on ${formatDate(dataset.created_at)}</span>
                                        </div>
                                    </div>
                                    <div class="d-flex">
                                        <a href="${dataset.url}" class="btn btn-sm btn-outline-primary me-2">
                                            <i data-feather="eye"></i> View Dataset
                                        </a>
                                        <a href="/dataset/download/${dataset.id}" class="btn btn-sm btn-outline-success">
                                            <i data-feather="download"></i> Download (${dataset.total_size_in_human_format})
                                        </a>
                                    </div>
                                </div>
                            </div>
                        `;
                        document.getElementById('results').appendChild(card);
                        updateAverageRating(dataset.id);
                    });
                });
        });
    });
}

function formatDate(dateString) {
    const options = {day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric'};
    const date = new Date(dateString);
    return date.toLocaleString('en-US', options);
}

function set_tag_as_query(tagName) {
    const queryInput = document.getElementById('query');
    queryInput.value = tagName.trim();
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

function set_publication_type_as_query(publicationType) {
    const publicationTypeSelect = document.getElementById('publication_type');
    for (let i = 0; i < publicationTypeSelect.options.length; i++) {
        if (publicationTypeSelect.options[i].text === publicationType.trim()) {
            publicationTypeSelect.value = publicationTypeSelect.options[i].value;
            break;
        }
    }
    publicationTypeSelect.dispatchEvent(new Event('input', {bubbles: true}));
}

document.getElementById('clear-filters').addEventListener('click', clearFilters);

function clearFilters() {
    let queryInput = document.querySelector('#query');
    queryInput.value = "";
    let publicationTypeSelect = document.querySelector('#publication_type');
    publicationTypeSelect.value = "any";
    let queryInputAuthor = document.querySelector('#queryAuthor');
    queryInputAuthor.value = "";
    let queryInputTag = document.querySelector('#queryTag');
    queryInputTag.value = "";
    let queryInputModels = document.querySelector('#queryModels');
    queryInputModels.value = "";
    let queryInputFeatures = document.querySelector('#queryFeatures');
    queryInputFeatures.value = "";
    let sortingOptions = document.querySelectorAll('[name="sorting"]');
    sortingOptions.forEach(option => {
        option.checked = option.value == "newest";
    });
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

document.addEventListener('DOMContentLoaded', () => {
    let urlParams = new URLSearchParams(window.location.search);
    let queryParam = urlParams.get('query');
    if (queryParam && queryParam.trim() !== '') {
        const queryInput = document.getElementById('query');
        queryInput.value = queryParam;
        queryInput.dispatchEvent(new Event('input', {bubbles: true}));
    } else {
        const queryInput = document.getElementById('query');
        queryInput.dispatchEvent(new Event('input', {bubbles: true}));
    }
});

function updateAverageRating(datasetId) {
    fetch(`/datasets/${datasetId}/average-rating`)
        .then(response => response.json())
        .then(data => {
            const ratingValue = data.average_rating.toFixed(1);
            document.getElementById('average-rating-' + datasetId).innerText = ratingValue;
            const starContainer = document.getElementById('star-rating-' + datasetId);
            highlightStars(starContainer, Math.round(data.average_rating));
        })
        .catch(error => console.error('Error fetching average rating:', error));
}

function highlightStars(container, rating) {
    container.querySelectorAll('span').forEach(star => {
        const starValue = star.getAttribute('data-value');
        star.style.color = starValue <= rating ? '#FFD700' : '#ddd';
    });
}