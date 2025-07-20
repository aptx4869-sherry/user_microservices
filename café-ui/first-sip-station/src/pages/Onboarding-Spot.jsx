import React from 'react';
import GuestCardForm from '../components/Guest-Card-Form.jsx'; 
import useToastPour from '../hooks/use-toast-pour';
import useGoogleBrew from '../hooks/use-google-brew'; 

function OnboardingSpot({ onGoogleSignInSuccess, onGoogleSignInError }) {
  const showToast = useToastPour();
  useGoogleBrew(onGoogleSignInSuccess, onGoogleSignInError);

  const handleTraditionalRegistrationSuccess = () => {
    showToast('🎉 Welcome aboard, new guest! Your profile is brewed and ready.', 'success');
  };

  const handleTraditionalRegistrationError = (error) => {
    showToast(`Oops! Something spilled during registration: ${error.message || 'Unknown error.'}`, 'error');
  };

  return (
    <div className="onboarding-spot bg-amber-50 p-6 rounded-lg shadow-inner border border-amber-200">
      <h2 className="text-3xl font-semibold text-amber-700 mb-6 text-center">Sign In or Get Your Guest Pass</h2>

      {/* Google Sign-In Button */}
      <div className="flex justify-center mb-8">
        <div id="g_id_signin" className="w-full max-w-xs"></div>
      </div>

      <div className="flex items-center justify-center my-6">
        <div className="border-t border-amber-300 flex-grow"></div>
        <span className="px-4 text-amber-600 text-sm">OR</span>
        <div className="border-t border-amber-300 flex-grow"></div>
      </div>

      {/* Traditional Registration Form (Optional) */}
      <h3 className="text-xl font-medium text-amber-700 mb-4 text-center">Register with Email & Password</h3>
      <GuestCardForm
        onSuccess={handleTraditionalRegistrationSuccess}
        onError={handleTraditionalRegistrationError}
      />

      <p className="text-center text-amber-600 mt-6 text-sm">Already have a Guest Pass? <a href="#" className="text-amber-800 hover:underline font-medium">Login here!</a></p>
    </div>
  );
}

export default OnboardingSpot;
