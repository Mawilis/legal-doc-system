import useTenants from './useTenants';

export default function useSovereignData() {
  const tenants = useTenants() || { activeTenant: 'MASTER' };
  return {
    activeTenant: tenants.activeTenant || 'MASTER',
    loading: false,
    error: null,
    data: tenants
  };
}
