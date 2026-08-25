import { useContext } from 'react';
import { DashboardStateContext } from '../providers/DashboardStateProvider.jsx';
export const useDashboardState = () => useContext(DashboardStateContext);
export default useDashboardState;
