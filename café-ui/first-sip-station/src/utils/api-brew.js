const API_BASE_URL = 'http://localhost:8000';
const API_TIMEOUT_MS = 10000;

/**
 * Helper function to fetch with a timeout.
 * @param {string} url - The URL to fetch.
 * @param {Object} options - Fetch options.
 * @param {number} timeout - Timeout in milliseconds.
 * @returns {Promise<Response>} The fetch response.
 */
async function fetchWithTimeout(url, options = {}, timeout = API_TIMEOUT_MS) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error('Request timed out');
        }
        throw error;
    }
}

/**
 * Fetches the Google Client ID from the backend.
 * @returns {Promise<string>} The Google Client ID.
 */
export async function fetchGoogleClientId() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/config/google-client-id`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to fetch Google Client ID: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        return data.client_id;
    } catch (error) {
        console.error("Error fetching Google Client ID:", error);
        throw error;
    }
}

/**
 * Sends the Google ID token to the backend for verification and session creation.
 * @param {string} token - The Google ID token.
 * @returns {Promise<Object>} The backend response data.
 */
export async function sendGoogleTokenToBackend(token) {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/google-register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: token }),
            credentials: "include" // Important for sending cookies
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || `Backend error: ${response.statusText}`);
        }
        return data;
    } catch (error) {
        console.error("Error sending Google token to backend:", error);
        throw error;
    }
}

/**
 * Checks if a user has an existing valid session with the backend using the session cookie.
 * @returns {Promise<Object>} The session data if valid, otherwise throws an error.
 */
export async function checkBackendSession() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/cookie-validate`, {
            credentials: "include" // Important for sending cookies
        });
        if (!response.ok) {
            // If not OK, it means no valid session or an error.
            const errorData = await response.json().catch(() => ({ message: response.statusText }));
            throw new Error(errorData.detail || `Session check failed: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Network or unexpected error during session validation:", error);
        throw error;
    }
}

/**
 * Refreshes the authentication token with the backend.
 * @returns {Promise<Object>} The refresh response data.
 */
export async function refreshToken() {
    try {
        const csrfToken = getCookie("csrf_token"); // Helper to get CSRF token from cookies

        const response = await fetchWithTimeout(`${API_BASE_URL}/auth/refresh`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken || "", // Include CSRF token for security
            },
            credentials: "include", // Important for sending cookies
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || `Token refresh failed: ${response.status} ${response.statusText}`);
        }
        return data;
    } catch (error) {
        console.error("Error refreshing token:", error);
        throw error;
    }
}

/**
 * Logs out the user by invalidating the session on the backend.
 * @returns {Promise<void>}
 */
export async function logoutUser() {
    try {
        const csrfToken = getCookie("csrf_token");
        const response = await fetchWithTimeout(`${API_BASE_URL}/auth/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken || "",
            },
            credentials: "include",
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Logout failed: ${response.status} ${response.statusText}`);
        }
        console.log("Logout successful.");
    } catch (error) {
        console.error("Error during logout:", error);
        throw error;
    }
}


/**
 * Helper function to get a cookie by name.
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string | undefined} The cookie value, or undefined if not found.
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return undefined;
}
