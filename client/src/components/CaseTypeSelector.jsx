import React from 'react';
import styled from 'styled-components';

const Grid = styled.div` display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; `;
const TypeCard = styled.div` 
  background: white; 
  padding: 30px; 
  border-radius: 12px; 
  border: 2px solid transparent; 
  box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
  cursor: pointer; 
  transition: all 0.2s; 
  text-align: center; 
  position: relative;
  &:hover { transform: translateY(-5px); border-color: #007bff; box-shadow: 0 8px 15px rgba(0, 123, 255, 0.15); } 
`;
const Icon = styled.div` font-size: 2.5rem; margin-bottom: 15px; `;
const Title = styled.h3` margin: 0 0 10px 0; color: #333; `;
const Desc = styled.p` color: #666; font-size: 0.9rem; line-height: 1.4; `;
const AdminBadge = styled.span`
  position: absolute; top: 10px; right: 10px; background: #000; color: #fff; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: bold;
`;

const TYPES = [
  { id: 'sheriff', label: 'Sheriff Service', icon: '🚔', desc: 'Dispatch & Execution Instructions', admin: true }, // <--- FORCED TOP
  { id: 'divorce', label: 'Family Law / Divorce', icon: '💍', desc: 'Settlement Agreements, Rule 43' },
  { id: 'litigation', label: 'General Litigation', icon: '⚖️', desc: 'Summons, Pleas, and Court Notices' },
  { id: 'property', label: 'Property Transfer', icon: '🏠', desc: 'Conveyancing and Lease Agreements' },
  { id: 'commercial', label: 'Commercial Contract', icon: '🤝', desc: 'NDAs, SLAs, and MOUs' },
  { id: 'debt', label: 'Debt Collection', icon: '💸', desc: 'Letters of Demand (Sec 129)' },
];

export default function CaseTypeSelector({ onSelect }) {
  return (
    <div>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <div>
           <h2 style={{color:'#333', marginBottom:'5px'}}>New Instruction</h2>
           <p style={{color:'#666'}}>Select the type of legal matter to initiate.</p>
        </div>
        <div style={{background:'#eef2ff', color:'#3730a3', padding:'5px 10px', borderRadius:'6px', fontSize:'0.8rem', fontWeight:'bold'}}>
           SYSTEM ADMIN MODE
        </div>
      </div>
      
      <Grid>
        {TYPES.map(type => (
          <TypeCard key={type.id} onClick={() => onSelect(type.id)} style={type.id === 'sheriff' ? {borderColor: '#2563eb', background:'#f0f9ff'} : {}}>
            {type.admin && <AdminBadge>New</AdminBadge>}
            <Icon>{type.icon}</Icon>
            <Title>{type.label}</Title>
            <Desc>{type.desc}</Desc>
          </TypeCard>
        ))}
      </Grid>
    </div>
  );
}
