import React from 'react';

const OperationsDashboard = ({ onLogout, tenantConfig }) => {
  return (
    <div className="flex items-center justify-center h-full w-full bg-black">
      <div className="text-center p-8">
        <h1 className="text-2xl font-black text-yellow-500 uppercase mb-4">OPERATIONS DASHBOARD</h1>
        <p className="text-stone-400">Workflow management and process optimization</p>
        <p className="text-stone-500 text-sm mt-2">Tenant: {tenantConfig?.name || 'WILSY OS'}</p>
        <button onClick={onLogout} className="mt-6 px-4 py-2 border border-red-800 text-red-400 text-xs uppercase rounded">Logout</button>
      </div>
    </div>
  );
};

export default OperationsDashboard;
