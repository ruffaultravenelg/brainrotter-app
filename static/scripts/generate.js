const loader = document.getElementById('loader');
const progress = document.getElementById('progress');
const download = document.getElementById('download');
const downloadBtn = document.getElementById('downloadBtn');

/**
 * Updates the progress bar value between 0 and 100.
 * @param {number} value - Progress percentage (0 to 100).
 */
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
function updateProgressBar(value) {
    const clampedValue = Math.min(100, Math.max(0, value));

    progressBar.style.width = `${clampedValue}%`;
    progressText.textContent = `${clampedValue}%`;
}

// Retrieve the 'prompt' query parameter
const urlParams = new URLSearchParams(window.location.search);
const prompt = urlParams.get('prompt');
if (!prompt) window.location.href = '/';

const statesContainer = document.getElementById('states');
let currentCardIndex = 0;
let cardElements = [];

/**
 * Creates and appends a new step card.
 * @param {number} index - The step index.
 * @param {Object} cardInfo - Information about the step.
 */
function createStepCard(index, cardInfo) {
    const card = document.createElement('div');
    card.className = 'card pending';
    card.style.animationDelay = `${index * 0.1}s`;

    card.innerHTML = `
        <p class="card-step">#${index + 1}</p>
        <p class="card-name">${cardInfo.name}</p>
        <p class="card-description">${cardInfo.description}</p>
    `;

    statesContainer.appendChild(card);
    cardElements.push(card);
}

/**
 * Renders all step cards.
 * @param {Array} steps - List of step objects.
 */
function renderStepCards(steps) {
    statesContainer.innerHTML = '';
    cardElements = [];
    currentCardIndex = -1;

    loader.hidden = true;
    progress.style.display = '';
    steps.forEach((step, index) => createStepCard(index, step));

    moveToNextStep();
}

/**
 * Updates card status (pending, active, completed).
 * @param {number} index - Card index to update.
 * @param {string} status - New status class ('pending', 'active', 'completed').
 */
function setCardStatus(index, status) {
    if (index < 0 || index >= cardElements.length) return;

    cardElements[index].className = `card ${status}`;
}

/**
 * Moves to the next step, updates progress bar, and scrolls to active card.
 */
function moveToNextStep() {
    if (currentCardIndex >= 0)
        setCardStatus(currentCardIndex, 'completed');
    currentCardIndex++;

    if (currentCardIndex < cardElements.length) {
        setCardStatus(currentCardIndex, 'active');
        scrollToCard(currentCardIndex);
    }

    const progress = Math.floor(((currentCardIndex + 1) / cardElements.length) * 100);
    updateProgressBar(progress);
}

/**
 * Scrolls the container so the active card is always aligned to the right of the screen.
 * @param {number} index - Index of the card to scroll to.
 */
function scrollToCard(index) {
    const card = cardElements[index];
    if (card) {
        const cardRightPosition = card.offsetLeft - (card.offsetWidth / 2);
        statesContainer.scrollTo({ left: cardRightPosition, behavior: 'smooth' });
    }
}

// SSE Connection
const eventSource = new EventSource(`/api/generate?prompt=${encodeURIComponent(prompt)}`);

// SSE Event Handlers
eventSource.onmessage = async (event) => {
    const data = event.data.toString();
    
    if (data.startsWith('[INFOS] ')) {
        const steps = JSON.parse(data.substring(7));
        renderStepCards(steps);
        progress.style.opacity = '';
    } else if (data.startsWith('[NEXT]')) {
        moveToNextStep();
    } else if (data.startsWith('[FILE] ')) {
        eventSource.close();
        const fileID = data.substring(7);
        finsish(fileID);
    } else if (data.startsWith('[ERROR] ')) {
        eventSource.close();
        await swal("Petit problème", data.substring(8), "error");
        window.location.href = '/';
    }
};

// Handle errors
eventSource.onerror = async (err) => {
    await swal("Petit problème", err.message, "error");
    window.location.href = '/';
};

// Finish
function finsish(fileID) {
    const link = `/api/download/${fileID}`;

    setTimeout(() => {
        progress.classList.add("hidding");
        
        setTimeout(() => {
            download.classList.add('active');
        }, 600);

    }, 400);

    downloadBtn.onclick = () => {
        window.open(link, '_blank');
    };
}
