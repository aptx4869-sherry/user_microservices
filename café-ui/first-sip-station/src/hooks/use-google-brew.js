import { useEffect, useCallback, useRef } from 'react';
import { fetchGoogleClientId, sendGoogleTokenToBackend } from '../utils/api-brew';
import useToastPour from './use-toast-pour';

/**
 * Custom hook to handle Google Sign-In (GSI) integration.
 * It initializes GSI, renders the Google button, and processes the credential response.
 * @param {function} onSignInSuccess - Callback function for successful sign-in.
 * @param {function} onSignInError - Callback function for sign-in errors.
 */
function useGoogleBrew(onSignInSuccess, onSignInError) {
    const showToast = useToastPour();
    // Use a ref to ensure GSI initialization happens only once
    const isGsiInitialized = useRef(false);

    // This function will be called by the Google Identity Services library
    const handleCredentialResponse = useCallback(async (response) => {
        console.log("🔵 handleCredentialResponse triggered.");
        if (response.credential) {
            try {
                const backendData = await sendGoogleTokenToBackend(response.credential);
                console.log("Backend response for Google login:", backendData);
                showToast("Welcome back! ☕ Session is warm and ready.", "success");
                onSignInSuccess(backendData); // Pass backend data to success callback
            } catch (err) {
                console.error("Error during Google login process:", err);
                showToast(`Google login failed: ${err.message}`, "error");
                onSignInError(err);
            }
        } else {
            console.error("Google credential response missing.");
            showToast("Google login failed: No credential received.", "error");
            onSignInError(new Error("No credential received from Google."));
        }
    }, [onSignInSuccess, onSignInError, showToast]);

    useEffect(() => {
        console.log("🔂 useGoogleBrew useEffect running (Component Mount/Update)");

        // Expose the callback globally for GSI library
        window.handleCredentialResponse = handleCredentialResponse;

        // Function to initialize GSI client and render button
        const initializeGsi = async () => {
            console.log("Attempting to initialize GSI...");
            // Ensure this runs only once
            if (isGsiInitialized.current) {
                console.log("GSI already initialized, skipping further initialization.");
                return;
            }

            // Check if Google GSI library is available
            if (!window.google || !window.google.accounts || !window.google.accounts.id) {
                console.log("Google GSI library not yet available. Retrying on next check/onload.");
                return; // Not ready yet, will be called again by script.onload
            }

            try {
                console.log("🟡 Fetching Google Client ID...");
                const googleClientId = await fetchGoogleClientId(); // Fetch from backend
                console.log("✅ Google Client ID fetched:", googleClientId);

                if (!googleClientId) {
                    throw new Error("Google Client ID was empty from backend. Check .env file.");
                }

                console.log("Initializing google.accounts.id with client_id:", googleClientId);
                window.google.accounts.id.initialize({
                    client_id: googleClientId,
                    callback: window.handleCredentialResponse,
                    // auto_select: true, // You might enable this later for One Tap
                    // cancel_on_tap_outside: false, // Useful for One Tap debugging
                });

                // Render the Google Sign-In button
                const signInButtonDiv = document.getElementById("g_id_signin");
                if (signInButtonDiv) {
                    console.log("Rendering Google Sign-In button...");
                    window.google.accounts.id.renderButton(
                        signInButtonDiv,
                        {
                            type: "standard",
                            theme: "outline",
                            size: "large",
                            shape: "rectangular",
                            text: "signin_with",
                            logo_alignment: "left"
                        }
                    );
                    console.log("Google Sign-In button rendered.");
                } else {
                    console.warn("Div with id 'g_id_signin' not found. Google Sign-In button may not render.");
                }

                // IMPORTANT: Comment out or remove window.google.accounts.id.prompt()
                // if you only want the button and not the One Tap prompt.
                // One Tap can trigger early gsi/status calls.
                // window.google.accounts.id.prompt(); 
                // console.log("Google One Tap prompt initiated. (If enabled)");

                isGsiInitialized.current = true; // Mark GSI as initialized
                console.log("GSI initialization complete.");

            } catch (e) {
                console.error("Error setting up Google Sign-In:", e);
                showToast(`Failed to load Google login: ${e.message}`, "error");
            }
        };

        // --- Primary trigger for GSI initialization ---
        // This handles cases where the GSI script loads very quickly
        // or is cached before the useEffect fully runs.
        initializeGsi();

        // --- Fallback trigger for GSI initialization ---
        // This handles cases where the GSI script loads after the useEffect runs.
        const script = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
        if (script) {
            // Only set onload if the script hasn't fully loaded and processed GSI object yet
            if (!window.google || !window.google.accounts || !window.google.accounts.id) {
                console.log("Setting script.onload for GSI initialization.");
                script.onload = initializeGsi;
                script.onerror = () => {
                    console.error("Failed to load Google Identity Services script.");
                    showToast("Failed to load Google Sign-In. Please try again.", "error");
                };
            } else {
                console.log("GSI script already loaded and object available. No onload needed.");
            }
        } else {
            console.error("Google Identity Services script tag not found in HTML.");
            showToast("Google Sign-In script missing from page.", "error");
        }

        // Cleanup: remove the global function and event listeners when component unmounts
        return () => {
            console.log("🔄 useGoogleBrew cleanup running");
            delete window.handleCredentialResponse;
            if (script) {
                script.onload = null; // Clean up event listener
                script.onerror = null;
            }
            // Optional: Explicitly cancel any ongoing GSI processes on unmount
            // if (window.google && window.google.accounts && window.google.accounts.id && isGsiInitialized.current) {
            //     window.google.accounts.id.cancel();
            //     console.log("GSI process cancelled on component unmount.");
            // }
        };
    }, [handleCredentialResponse, showToast]); // Dependencies for useEffect
}

export default useGoogleBrew;
