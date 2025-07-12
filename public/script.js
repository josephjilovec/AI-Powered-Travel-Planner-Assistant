// public/script.js

// --- DOM Element References ---
const chatMessagesContainer = document.getElementById('chat-messages');
const userInputTextarea = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const loadingIndicator = document.getElementById('loading-indicator');
const errorMessageDisplay = document.getElementById('error-message');

const recommendationsTabButton = document.querySelector('.tab-button[data-tab="recommendations"]');
const itineraryTabButton = document.querySelector('.tab-button[data-tab="itinerary"]');
const recommendationsContent = document.getElementById('recommendations-content');
const itineraryContent = document.getElementById('itinerary-content');

const recommendedFlightsDiv = document.getElementById('recommended-flights');
const recommendedHotelsDiv = document.getElementById('recommended-hotels');
const recommendedActivitiesDiv = document.getElementById('recommended-activities');
const itineraryDetailsDiv = document.getElementById('itinerary-details');

// --- Session State Management ---
// A simple way to manage session ID for continuity with the backend.
// In a real app, this might involve user authentication and server-side session management.
let currentSessionId = localStorage.getItem('travelPlannerSessionId');
if (!currentSessionId) {
    currentSessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('travelPlannerSessionId', currentSessionId);
    console.log('New session ID generated:', currentSessionId);
} else {
    console.log('Existing session ID:', currentSessionId);
}

// Store the current trip context (preferences, recommendations, itinerary)
// This will be sent back to the backend for the /chat endpoint to provide context to the TripSupportAgent.
let currentTripContext = {
    preferences: {},
    recommendations: {},
    itinerary: []
};

// --- UI Utility Functions ---

/**
 * Displays a message in the chat interface.
 * @param {string} message - The text content of the message.
 * @param {'user'|'assistant'} role - The sender of the message.
 */
function displayChatMessage(message, role) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', role, 'max-w-[80%]', 'p-3', 'rounded-xl', 'shadow-sm');
    messageDiv.innerHTML = `<p>${message}</p>`; // Use innerHTML to allow basic formatting if needed
    chatMessagesContainer.appendChild(messageDiv);
    // Scroll to the bottom to show the latest message
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

/**
 * Shows a loading indicator and disables input.
 */
function showLoading() {
    loadingIndicator.classList.remove('hidden');
    sendButton.disabled = true;
    userInputTextarea.disabled = true;
    errorMessageDisplay.classList.add('hidden'); // Hide any previous errors
}

/**
 * Hides the loading indicator and enables input.
 */
function hideLoading() {
    loadingIndicator.classList.add('hidden');
    sendButton.disabled = false;
    userInputTextarea.disabled = false;
}

/**
 * Displays an error message to the user.
 * @param {string} message - The error message to display.
 */
function showErrorMessage(message) {
    errorMessageDisplay.textContent = message;
    errorMessageDisplay.classList.remove('hidden');
    // Hide after a few seconds
    setTimeout(() => {
        errorMessageDisplay.classList.add('hidden');
        errorMessageDisplay.textContent = '';
    }, 7000);
}

/**
 * Activates a specific tab in the results section.
 * @param {'recommendations'|'itinerary'} tabName - The name of the tab to activate.
 */
function activateTab(tabName) {
    // Remove 'active' class from all buttons and content
    recommendationsTabButton.classList.remove('active', 'text-blue-600', 'border-blue-600');
    recommendationsTabButton.classList.add('text-gray-600', 'hover:text-gray-800', 'border-transparent');
    itineraryTabButton.classList.remove('active', 'text-blue-600', 'border-blue-600');
    itineraryTabButton.classList.add('text-gray-600', 'hover:text-gray-800', 'border-transparent');

    recommendationsContent.classList.add('hidden');
    itineraryContent.classList.add('hidden');

    // Add 'active' class to the selected tab button and content
    if (tabName === 'recommendations') {
        recommendationsTabButton.classList.add('active', 'text-blue-600', 'border-blue-600');
        recommendationsTabButton.classList.remove('text-gray-600', 'hover:text-gray-800', 'border-transparent');
        recommendationsContent.classList.remove('hidden');
    } else if (tabName === 'itinerary') {
        itineraryTabButton.classList.add('active', 'text-blue-600', 'border-blue-600');
        itineraryTabButton.classList.remove('text-gray-600', 'hover:text-gray-800', 'border-transparent');
        itineraryContent.classList.remove('hidden');
    }
}

// --- Rendering Functions for Results ---

/**
 * Renders flight recommendations.
 * @param {Array<Object>} flights - List of recommended flights.
 */
function renderFlights(flights) {
    recommendedFlightsDiv.innerHTML = '<h4 class="font-bold text-blue-800 mb-2">Flights</h4>';
    if (flights.length === 0) {
        recommendedFlightsDiv.innerHTML += '<p class="text-gray-600">No flight recommendations found for your criteria.</p>';
        return;
    }
    flights.forEach(flight => {
        recommendedFlightsDiv.innerHTML += `
            <div class="recommendation-item">
                <p><strong>${flight.airline}</strong>: ${flight.origin} to ${flight.destination}</p>
                <p>Departure: ${flight.departure_date} at ${flight.departure_time}</p>
                ${flight.return_date ? `<p>Return: ${flight.return_date}</p>` : ''}
                <p>Price: $${flight.price ? flight.price.toFixed(2) : 'N/A'}</p>
            </div>
        `;
    });
}

/**
 * Renders hotel recommendations.
 * @param {Array<Object>} hotels - List of recommended hotels.
 */
function renderHotels(hotels) {
    recommendedHotelsDiv.innerHTML = '<h4 class="font-bold text-green-800 mb-2">Hotels</h4>';
    if (hotels.length === 0) {
        recommendedHotelsDiv.innerHTML += '<p class="text-gray-600">No hotel recommendations found for your criteria.</p>';
        return;
    }
    hotels.forEach(hotel => {
        recommendedHotelsDiv.innerHTML += `
            <div class="recommendation-item">
                <p><strong>${hotel.name}</strong> (${hotel.destination})</p>
                <p>Rating: ${hotel.rating} Stars</p>
                <p>Price/Night: $${hotel.price_per_night ? hotel.price_per_night.toFixed(2) : 'N/A'}</p>
                <p>Amenities: ${hotel.amenities ? hotel.amenities.join(', ') : 'N/A'}</p>
            </div>
        `;
    });
}

/**
 * Renders activity recommendations.
 * @param {Array<Object>} activities - List of recommended activities.
 */
function renderActivities(activities) {
    recommendedActivitiesDiv.innerHTML = '<h4 class="font-bold text-purple-800 mb-2">Activities</h4>';
    if (activities.length === 0) {
        recommendedActivitiesDiv.innerHTML += '<p class="text-gray-600">No activity recommendations found for your criteria.</p>';
        return;
    }
    activities.forEach(activity => {
        recommendedActivitiesDiv.innerHTML += `
            <div class="recommendation-item">
                <p><strong>${activity.name}</strong> (${activity.destination})</p>
                <p>Price: $${activity.price ? activity.price.toFixed(2) : 'N/A'}</p>
                <p>Duration: ${activity.duration_hours ? activity.duration_hours : 'N/A'} hours</p>
                <p>Tags: ${activity.tags ? activity.tags.join(', ') : 'N/A'}</p>
            </div>
        `;
    });
}

/**
 * Renders the full daily itinerary.
 * @param {Array<Object>} itinerary - The daily itinerary plan.
 */
function renderItinerary(itinerary) {
    itineraryDetailsDiv.innerHTML = ''; // Clear previous itinerary
    if (itinerary.length === 0) {
        itineraryDetailsDiv.innerHTML = '<p class="text-gray-600">No itinerary generated yet. Please provide your travel preferences in the chat!</p>';
        return;
    }

    itinerary.forEach(dayPlan => {
        const dayCard = document.createElement('div');
        dayCard.classList.add('itinerary-day-card');
        dayCard.innerHTML = `
            <h4 class="font-bold text-orange-700 mb-2">${dayPlan.date} - ${dayPlan.day_of_week} (${dayPlan.theme})</h4>
            <div class="itinerary-events-list"></div>
        `;
        const eventsList = dayCard.querySelector('.itinerary-events-list');
        dayPlan.events.forEach(event => {
            const eventDiv = document.createElement('div');
            eventDiv.classList.add('itinerary-event');
            let detailsHtml = '';
            if (event.details && Object.keys(event.details).length > 0) {
                detailsHtml = `<ul class="list-disc list-inside text-sm text-gray-700 mt-1">`;
                for (const key in event.details) {
                    detailsHtml += `<li>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${event.details[key]}</li>`;
                }
                detailsHtml += `</ul>`;
            }
            eventDiv.innerHTML = `
                <p><strong>${event.time}</strong>: ${event.description}</p>
                ${detailsHtml}
            `;
            eventsList.appendChild(eventDiv);
        });
        itineraryDetailsDiv.appendChild(dayCard);
    });
}

// --- API Interaction Functions ---

/**
 * Handles the initial trip planning request.
 */
async function planTrip() {
    const userQuery = userInputTextarea.value.trim();
    if (!userQuery) {
        showErrorMessage('Please tell me about your trip plans!');
        return;
    }

    displayChatMessage(userQuery, 'user');
    userInputTextarea.value = ''; // Clear input field
    showLoading();

    try {
        const response = await fetch('/plan_trip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userQuery, session_id: currentSessionId })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            hideLoading();
            displayChatMessage(result.message, 'assistant'); // "Trip plan generated!"

            // Store the full trip plan in session context
            currentTripContext = result.data;

            // Render recommendations
            renderFlights(currentTripContext.recommendations.recommended_flights || []);
            renderHotels(currentTripContext.recommendations.recommended_hotels || []);
            renderActivities(currentTripContext.recommendations.recommended_activities || []);

            // Render itinerary
            renderItinerary(currentTripContext.itinerary || []);

            // Activate the recommendations tab by default after a plan is generated
            activateTab('recommendations');

        } else {
            hideLoading();
            const errorMessage = result.message || 'An unknown error occurred during trip planning.';
            displayChatMessage(errorMessage, 'assistant');
            showErrorMessage(errorMessage);
            console.error('Plan trip API error:', result);
        }
    } catch (error) {
        hideLoading();
        displayChatMessage('I apologize, an unexpected error occurred. Please try again.', 'assistant');
        showErrorMessage(`Network error: ${error.message}`);
        console.error('Fetch error during planTrip:', error);
    }
}

/**
 * Handles ongoing chat messages for trip support.
 */
async function sendChatMessage() {
    const userMessage = userInputTextarea.value.trim();
    if (!userMessage) {
        showErrorMessage('Please type a message.');
        return;
    }

    displayChatMessage(userMessage, 'user');
    userInputTextarea.value = ''; // Clear input field
    showLoading();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Send the current trip context for the support agent
            body: JSON.stringify({ message: userMessage, session_id: currentSessionId, trip_context: currentTripContext })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            hideLoading();
            displayChatMessage(result.response, 'assistant');
            // Optionally, update UI based on action_suggested (e.g., "simulated_rebooking")
            if (result.action_suggested && result.action_suggested !== 'information_provided') {
                console.log('Action suggested by agent:', result.action_suggested);
                // You could add a visual cue here, like a small notification
            }
        } else {
            hideLoading();
            const errorMessage = result.message || 'An unknown error occurred during chat.';
            displayChatMessage(errorMessage, 'assistant');
            showErrorMessage(errorMessage);
            console.error('Chat API error:', result);
        }
    } catch (error) {
        hideLoading();
        displayChatMessage('I apologize, an unexpected error occurred. Please try again.', 'assistant');
        showErrorMessage(`Network error: ${error.message}`);
        console.error('Fetch error during sendChatMessage:', error);
    }
}

// --- Event Listeners ---

// Send button click
sendButton.addEventListener('click', async () => {
    // Determine whether to call planTrip or sendChatMessage based on current state
    // For simplicity, let's assume the first interaction is always 'plan_trip'
    // and subsequent interactions are 'chat'.
    // A more robust solution would involve checking if a trip is already planned.
    if (Object.keys(currentTripContext.preferences).length === 0) {
        await planTrip(); // Initial planning
    } else {
        await sendChatMessage(); // Ongoing support
    }
});

// Enter key in textarea
userInputTextarea.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent new line
        sendButton.click(); // Trigger send button click
    }
});

// Tab button clicks
recommendationsTabButton.addEventListener('click', () => activateTab('recommendations'));
itineraryTabButton.addEventListener('click', () => activateTab('itinerary'));

// --- Initial Setup ---
document.addEventListener('DOMContentLoaded', () => {
    // Activate the recommendations tab by default on page load
    activateTab('recommendations');
});
