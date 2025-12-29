import React from 'react';

export default function FooterSimple() {
  return (
    <footer style={{
      height:48, display:'flex', alignItems:'center', justifyContent:'center',
      borderTop:'1px solid #eee', background:'#fff'
    }}>
      <small>© {new Date().getFullYear()} LegalDocSys. All rights reserved.</small>
    </footer>
  );
}
