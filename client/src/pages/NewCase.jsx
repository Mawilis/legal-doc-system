import React, { useState } from 'react';
import styled from 'styled-components';
import { LITIGATION_TYPES } from '../data/litigationTypes';
import CaseTypeSelector from '../components/CaseTypeSelector';
import UniversalLegalForm from '../features/documents/pages/UniversalLegalForm';
import SheriffInstructionForm from '../features/documents/pages/SheriffInstructionForm'; 

const Container = styled.div` padding: 40px; max-width: 1400px; margin: 0 auto; background: #f4f6f8; min-height: 100vh; font-family: 'Inter', system-ui, sans-serif; `;
const Header = styled.div` margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; `;
const BackBtn = styled.button` background: white; border: 1px solid #ddd; padding: 8px 16px; border-radius: 6px; cursor: pointer; &:hover { background: #f8f9fa; } `;
const Grid = styled.div` display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; `;
const TypeCard = styled.div` background: white; padding: 25px; border-radius: 10px; border: 2px solid transparent; cursor: pointer; transition: all 0.2s; &:hover { transform: translateY(-3px); border-color: #2563eb; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.15); } text-align: center; `;

export default function NewCase() {
  const [step, setStep] = useState(1);
  const [mainCategory, setMainCategory] = useState(null);
  const [config, setConfig] = useState({});

  const handleMainSelect = (id) => {
    setMainCategory(id);
    
    // 1. SHERIFF ROUTE (PRIORITY)
    if (id === 'sheriff') {
       setStep(2); 
       return;
    }

    // 2. LITIGATION ROUTE
    if (id === 'litigation') {
       setStep(1.5); 
       return;
    }

    // 3. OTHER ROUTES
    if (id === 'divorce') setConfig({ label: 'Divorce Settlement', baseFee: 2500, classification: 'FAMILY', isDivorce: true });
    else if (id === 'property') setConfig({ label: 'Property Transfer', baseFee: 4500, classification: 'PROPERTY' });
    else if (id === 'commercial') setConfig({ label: 'Commercial Contract', baseFee: 3500, classification: 'COMMERCIAL' });
    else if (id === 'debt') setConfig({ label: 'Debt Collection', baseFee: 850, classification: 'LITIGATION' });
    else setConfig({ label: 'General Matter', baseFee: 1200, classification: 'GENERAL' });
    
    setStep(2);
  };

  const handleLitigationSubSelect = (subType) => {
      setConfig({ label: subType.label, baseFee: subType.baseFee || 2500, classification: 'LITIGATION', subType: subType.id });
      setStep(2);
  };

  // STEP 1.5: LITIGATION MENU
  if (step === 1.5) {
      return (
        <Container>
            <Header><BackBtn onClick={() => setStep(1)}>← Back</BackBtn><h1>Select Litigation Process</h1></Header>
            <Grid>{LITIGATION_TYPES.map(t => <TypeCard key={t.id} onClick={() => handleLitigationSubSelect(t)}><div style={{fontSize:'2.5rem'}}>{t.icon}</div><h3>{t.label}</h3></TypeCard>)}</Grid>
        </Container>
      );
  }

  // STEP 2: FORM RENDERER
  if (step === 2) {
    return (
       <>
         <div style={{maxWidth:'1400px', margin:'0 auto', padding:'20px 40px 0'}}><BackBtn onClick={() => setStep(1)}>← Change Type</BackBtn></div>
         {mainCategory === 'sheriff' ? (
             <SheriffInstructionForm /> 
         ) : (
             <UniversalLegalForm type={mainCategory} config={config} />
         )}
       </>
    );
  }

  return (
    <Container>
      <CaseTypeSelector onSelect={handleMainSelect} /> 
    </Container>
  );
}
