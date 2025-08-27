import React from 'react';

function GuestLounge({ username, onLogout }) {
  return (
    <div className="guest-lounge bg-amber-50 p-6 rounded-lg shadow-inner border border-amber-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-amber-700">
          Hello, <span className="text-amber-800 font-bold">{username}!</span>
        </h2>
        <button
          onClick={onLogout}
          className="bg-red-600 text-white py-2 px-4 rounded-md shadow-md hover:bg-red-700 transition duration-200 ease-in-out"
        >
          Logout
        </button>
      </div>

      <p className="text-amber-600 text-lg mb-4">
        Welcome to your personalized Coding Café experience. Your brew is ready!
      </p>
      <p className="text-amber-500 text-sm">
        This is your exclusive lounge where you can manage your preferences, explore new features, and enjoy your coding journey.
      </p>
      {/* Add more content for the authenticated user here */}
    </div>
  );
}

export default GuestLounge;
