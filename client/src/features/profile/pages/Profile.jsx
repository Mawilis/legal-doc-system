import React from 'react';

export default function Profile() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <div style={{padding:24}}>
      <h1>Profile</h1>
      <p>Lightweight Profile page is rendering. 👤</p>
      <pre style={{background:'#f7f7f7', padding:12, borderRadius:8, overflow:'auto'}}>
{JSON.stringify(user, null, 2)}
      </pre>
    </div>
  );
}
