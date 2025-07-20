import React, { useEffect, useState, useRef, useCallback } from 'react';
import OnboardingSpot from './pages/Onboarding-Spot.jsx'; 
import GuestLounge from './pages/Guest-Lounge.jsx'; 
import useToastPour from './hooks/use-toast-pour'; 
import { checkBackendSession, refreshToken, logoutUser } from './utils/api-brew'; 

function GrandBlend() {
  const showToast = useToastPour();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState(null); // To display welcome message
  const refreshTimeoutRef = useRef(null);

  // Callback for successful Google Sign-In
  const handleGoogleSignInSuccess = (backendData) => {
    setIsAuthenticated(true);
    setUsername(backendData.username || 'Guest'); 
    scheduleTokenRefresh(backendData.access_token); // Add this
  };

  // Callback for Google Sign-In errors
  const handleGoogleSignInError = () => {
    setIsAuthenticated(false);
    setUsername(null);
  };


  // Function to check session and display welcome toast
  const checkSessionAndShowToast = async () => {
    try {
      const sessionData = await checkBackendSession();
      setIsAuthenticated(true);
      setUsername(sessionData.username || 'Guest');
      showToast(`Welcome back ${sessionData.username || 'Guest'}! ☕`, "success");
      scheduleTokenRefresh(sessionData.access_token);
    } catch (err) {
      console.log("Session check failed (no valid session or error):", err.message);
      setIsAuthenticated(false);
      setUsername(null);
    }
  };

  // Handle user logout
  const handleLogout = async () => {
     try {
        if (refreshTimeoutRef.current) {
          clearTimeout(refreshTimeoutRef.current); // Cancel refresh timer
        }

        await logoutUser();
        setIsAuthenticated(false);
        setUsername(null);
        showToast("You've successfully logged out. See you soon! 👋", "success");
      } catch (error) {
    console.error("Logout failed:", error);
    showToast(`Logout failed: ${error.message || 'Unknown error.'}`, "error");
  }
  };

    const scheduleTokenRefresh = useCallback((accessToken) => {
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();
      const refreshIn = Math.max(exp - now - 2 * 60 * 1000, 60 * 1000);

      refreshTimeoutRef.current = setTimeout(async () => {
        try {
          const newToken = await refreshToken();
          scheduleTokenRefresh(newToken); // Reschedule for next token
          console.log("Token refreshed and rescheduled");
        } catch (err) {
          console.error("Refresh failed:", err);
          if (err.message.includes('401')) {
            showToast("Session expired. Please log in again.", "error");
            setIsAuthenticated(false);
            setUsername(null);
            setTimeout(() => window.location.reload(), 2000);
          }
        }
      }, refreshIn);
    } catch (e) {
      console.error("Failed to schedule token refresh:", e);
    }
  }, [showToast]);


  // Effect for initial session check on component mount
  useEffect(() => {
    checkSessionAndShowToast();
  }, []); // Run once on mount

  // Effect for refreshing token every 5 minutes
  useEffect(() => {
    const refreshInterval = setInterval(async () => {
      if (isAuthenticated) { // Only try to refresh if already authenticated
        try {
          const data = await refreshToken();
          console.log("Token refreshed in background:", data);
        } catch (err) {
          console.error("Refresh failed:", err);
          if (err.message.includes('401')) { // Check for unauthorized status
            showToast("Session expired. Please log in again.", "error");
            setIsAuthenticated(false);
            setUsername(null);
            setTimeout(() => window.location.reload(), 2000); // Reload to prompt login
          } else {
            showToast(`Failed to refresh session: ${err.message}`, "error");
          }
        }
      }
    }, 5 * 60 * 1000); // every 5 minutes

    // Cleanup interval on component unmount
    return () => clearInterval(refreshInterval);
  }, [isAuthenticated, showToast]); // Re-run if authentication status changes

  return (
     <div className="container bg-white p-8 rounded-xl shadow-2xl border border-amber-300 text-center">

      <main>
        {isAuthenticated ? (
          <GuestLounge username={username} onLogout={handleLogout} /> // Show guest lounge if authenticated
        ) : (
          <OnboardingSpot 
            onGoogleSignInSuccess={handleGoogleSignInSuccess}
            onGoogleSignInError={handleGoogleSignInError}/> // Show onboarding/login if not authenticated
        )}
      </main>
      <footer className="text-center mt-8 text-amber-500 text-sm">
        <p>&copy; 2025 Coding Café. All rights reserved. Brewed with care.</p>
      </footer>
    </div>
  );
}

export default GrandBlend;
