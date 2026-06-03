import React from 'react';

const WelcomePortal = ({ onInitialize }) => {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-neutral-950 text-white p-6">
      <div className="relative z-10 flex flex-col items-center space-y-12">
        <h1
          data-testid="auth-portal-title"
          className="text-6xl md:text-8xl font-black tracking-[0.3em] uppercase leading-tight text-center"
        >
          WELCOME TO
          <br />
          <span
            className="text-yellow-600 drop-shadow-[0_0_40px_rgba(202,138,4,0.3)] animate-pulse"
          >
            THE CITADEL
          </span>
        </h1>

        <button
          data-testid="initialize-gate-btn"
          onClick={onInitialize}
          className="px-12 py-4 border-2 border-yellow-600 text-yellow-600 font-black tracking-[0.5em] uppercase hover:bg-yellow-600 hover:text-black transition-all duration-500"
        >
          INITIALIZE_GATE
        </button>
      </div>
    </div>
  );
};

export default WelcomePortal;
