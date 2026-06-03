/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { getFirms as fetchUsers } from '../../api/superadmin'; // Aligning naming with Billion-Dollar standards

const Users = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchUsers();
        setUsers(data.firms || []);
      } catch (e) { console.error("Sovereign Error: Data fetch failed."); }
    };
    loadData();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">User Management</h1>
      <table className="w-full mt-4">
        <tbody>
          <tr><td>admin@wilsy.co.za</td></tr>
        </tbody>
      </table>
    </div>
  );
};

export default Users;
