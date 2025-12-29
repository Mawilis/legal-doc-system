import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

const Wrapper = styled.div` position: relative; width: 100%; `;
const StyledInput = styled.input` width: 100%; padding: 12px; border: 1px solid ${props => props.$error ? '#dc2626' : '#cbd5e1'}; border-radius: 6px; font-size: 0.95rem; background: #fff; &:focus { outline: none; border-color: #2563eb; } `;
const Suggestions = styled.ul` position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 4px; padding: 0; list-style: none; z-index: 100; max-height: 250px; overflow-y: auto; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); `;
const Item = styled.li` padding: 12px 15px; cursor: pointer; font-size: 0.9rem; border-bottom: 1px solid #f3f4f6; &:hover { background: #eff6ff; color: #2563eb; } strong { font-weight: 600; color: #111; } `;

const SA_PLACES = [
  { street: '100 Rivonia Road', city: 'Sandton', province: 'Gauteng', code: '2196' },
  { street: '15 Alice Lane', city: 'Sandton', province: 'Gauteng', code: '2196' },
  { street: '50 Church Square', city: 'Pretoria', province: 'Gauteng', code: '0002' },
  { street: '7 Hout Street', city: 'Cape Town', province: 'Western Cape', code: '8000' },
  { street: '200 Florida Road', city: 'Durban', province: 'KwaZulu-Natal', code: '4001' }
];

export default function AddressAutocomplete({ value, onChange, onSelect, error, name }) {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState([]);
  const [show, setShow] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => { setQuery(value || ''); }, [value]);

  useEffect(() => {
    function handleClickOutside(event) { if (wrapperRef.current && !wrapperRef.current.contains(event.target)) setShow(false); }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleInput = (e) => {
    const val = e.target.value;
    setQuery(val);
    onChange(e); 
    if (val.length > 1) {
      setResults(SA_PLACES.filter(p => p.street.toLowerCase().includes(val.toLowerCase()) || p.city.toLowerCase().includes(val.toLowerCase())));
      setShow(true);
    } else { setShow(false); }
  };

  return (
    <Wrapper ref={wrapperRef}>
      <StyledInput name={name} value={query} onChange={handleInput} placeholder="Start typing address..." autoComplete="off" $error={!!error} />
      {show && results.length > 0 && (
        <Suggestions>
          {results.map((r, i) => (
            <Item key={i} onClick={() => { setQuery(r.street); setShow(false); onSelect(r); }}>
              <div><strong>{r.street}</strong>, {r.city}</div>
            </Item>
          ))}
        </Suggestions>
      )}
    </Wrapper>
  );
}