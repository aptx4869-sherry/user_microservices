import { useCallback } from 'react';


const Toastify = window.Toastify;

/**
 * Custom hook to display themed toast notifications.
 * @returns {function(string, string): void} The showToast function.
 */
function useToastPour() {
    const showToast = useCallback((message, type = "success") => {
        if (!Toastify) {
            console.warn("Toastify-JS not loaded. Cannot display toast:", message);
            return;
        }

        let backgroundColor;
        switch (type) {
            case "success":
                backgroundColor = "#6f4e37"; // Coffee brown for success
                break;
            case "error":
                backgroundColor = "#FF5733"; // Red-orange for error
                break;
            default:
                backgroundColor = "#5e412f"; // Default/info, currently same as success.
        }

        Toastify({
            text: message,
            duration: 3000,
            gravity: "top",
            position: "center",
            backgroundColor: backgroundColor,
            stopOnFocus: true,
        }).showToast();
    }, []);

    return showToast;
}

export default useToastPour;