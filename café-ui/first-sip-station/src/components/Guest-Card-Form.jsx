import React, { useState } from 'react';
import useToastPour from '../hooks/use-toast-pour'; 

function GuestCardForm({ onSuccess, onError }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const showToast = useToastPour(); 

  const handleSubmit = async (e) => {
    e.preventDefault(); 
    setLoading(true); 

    try {

      await new Promise(resolve => setTimeout(resolve, 1500));

      console.log('Simulated traditional registration success:', { username, email, password });
      onSuccess(); 

      setUsername('');
      setEmail('');
      setPassword('');

    } catch (error) {
      console.error('Traditional registration failed:', error);
      onError(error); 
      showToast(`Traditional registration failed: ${error.message || 'Unknown error.'}`, 'error');
    } finally {
      setLoading(false); // Brewing process complete!
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="username" className="block text-amber-800 text-sm font-medium mb-2">
          Your Café Nickname
        </label>
        <input
          type="text"
          id="username"
          className="w-full px-4 py-2 border border-amber-300 rounded-md shadow-sm focus:ring-amber-500 focus:border-amber-500 transition duration-150 ease-in-out"
          placeholder="e.g., CodeBrewMaster"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-amber-800 text-sm font-medium mb-2">
          Your Email Address
        </label>
        <input
          type="email"
          id="email"
          className="w-full px-4 py-2 border border-amber-300 rounded-md shadow-sm focus:ring-amber-500 focus:border-amber-500 transition duration-150 ease-in-out"
          placeholder="e.g., guest@codingcafe.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-amber-800 text-sm font-medium mb-2">
          Choose Your Secret Brew Code
        </label>
        <input
          type="password"
          id="password"
          className="w-full px-4 py-2 border border-amber-300 rounded-md shadow-sm focus:ring-amber-500 focus:border-amber-500 transition duration-150 ease-in-out"
          placeholder="At least 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength="8"
        />
      </div>
      <button
        type="submit"
        className="w-full bg-amber-600 text-white py-3 px-4 rounded-lg font-semibold text-lg shadow-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 transition duration-200 ease-in-out flex items-center justify-center"
        disabled={loading}
      >
        {loading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Brewing Your Pass...
          </>
        ) : (
          'Get Your Guest Pass!'
        )}
      </button>
    </form>
  );
}

export default GuestCardForm;