// ~/client/src/features/instructions/pages/Instructions.jsx

import React, { useEffect, useState, useMemo } from 'react';
import styled from 'styled-components';
import { useSelector, useDispatch } from 'react-redux';
import { fetchInstructions } from '../reducers/instructionSlice'; // Assuming this thunk exists
import InstructionItem from '../../../components/InstructionItem'; // The masterpiece item component
import LoadingSpinner from '../../../components/LoadingSpinner';
import Button from '../../../components/atoms/Button';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { FaFilePdf } from 'react-icons/fa';

// --- Styled Components for the Page Layout ---

const PageWrapper = styled.div`
  padding: 2rem;
`;

const PageHeader = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  padding-bottom: 1.5rem;
`;

const PageTitle = styled.h1`
  font-size: 2.5rem;
  color: ${({ theme }) => theme.colors.text || '#333'};
  margin: 0;
`;

const FilterToolbar = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.background || '#ffffff'};
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
`;

const SearchInput = styled.input`
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 250px;
`;

const DateInput = styled(SearchInput)``;

const ErrorText = styled.p`
  color: ${({ theme }) => theme.colors.danger || '#dc3545'};
  text-align: center;
  font-size: 1.2rem;
`;

/**
 * The main page for displaying, filtering, and exporting a list of instructions.
 */
const Instructions = () => {
    const dispatch = useDispatch();
    const { instructions, loading, error } = useSelector((state) => state.instructions);

    // --- State for Filters ---
    const [search, setSearch] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // Fetch instructions when the component mounts
    useEffect(() => {
        dispatch(fetchInstructions());
    }, [dispatch]);

    // --- Memoized Filtering Logic for Performance ---
    const filteredInstructions = useMemo(() => {
        return instructions.filter(instruction => {
            const matchesSearch = instruction.title.toLowerCase().includes(search.toLowerCase());

            const instructionDate = new Date(instruction.createdAt);
            const start = startDate ? new Date(startDate) : null;
            const end = endDate ? new Date(endDate) : null;

            // Adjust end date to include the entire day
            if (end) end.setHours(23, 59, 59, 999);

            const inRange = (!start || start <= instructionDate) && (!end || end >= instructionDate);

            return matchesSearch && inRange;
        });
    }, [instructions, search, startDate, endDate]);

    /**
     * Exports the currently visible (filtered) instructions to a PDF.
     */
    const exportToPDF = () => {
        const content = document.getElementById('pdf-content');
        if (!content) return;

        html2canvas(content).then((canvas) => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save('instructions-report.pdf');
        });
    };

    // --- Render Logic ---
    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorText>Error: {error}</ErrorText>;

    return (
        <PageWrapper>
            <PageHeader>
                <PageTitle>Instructions</PageTitle>
                <Button onClick={exportToPDF} variant="secondary">
                    <FaFilePdf /> Export to PDF
                </Button>
            </PageHeader>

            <FilterToolbar>
                <SearchInput
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="🔍 Search by title..."
                />
                <DateInput
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                />
                <DateInput
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                />
            </FilterToolbar>

            {/* This div wraps the content that will be exported to PDF */}
            <div id="pdf-content">
                {filteredInstructions.length > 0 ? (
                    filteredInstructions.map((inst) => (
                        <InstructionItem key={inst._id} instruction={inst} />
                    ))
                ) : (
                    <p>No instructions match your criteria.</p>
                )}
            </div>
        </PageWrapper>
    );
};

export default Instructions;
