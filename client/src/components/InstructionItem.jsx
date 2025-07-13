import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'; // Import icons for toggle

const InstructionItem = ({ instruction }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    // Toggle the display of more details
    const toggleDetails = () => {
        setIsExpanded(!isExpanded);
    };

    return (
        <InstructionContainer>
            <InstructionHeader>
                <Title>{instruction.title}</Title> {/* Display the instruction title */}
                <ToggleButton onClick={toggleDetails} aria-expanded={isExpanded}> {/* Add aria-expanded for accessibility */}
                    {isExpanded ? <FaChevronUp /> : <FaChevronDown />} {/* Use icons for better visual indication */}
                    {isExpanded ? 'Hide Details' : 'Show Details'}
                </ToggleButton>
            </InstructionHeader>

            {/* Conditionally render instruction details when isExpanded is true */}
            {isExpanded && (
                <InstructionDetails>
                    <Content>{instruction.content}</Content> {/* Display the instruction content */}
                    <MetaInfo>
                        <span>Created by: {instruction.creator}</span> {/* Display who created the instruction */}
                        <span>Date: {new Date(instruction.createdAt).toLocaleDateString()}</span> {/* Display the creation date */}
                    </MetaInfo>
                </InstructionDetails>
            )}
        </InstructionContainer>
    );
};

// PropTypes for validation
InstructionItem.propTypes = {
    instruction: PropTypes.shape({
        title: PropTypes.string.isRequired,
        content: PropTypes.string.isRequired,
        creator: PropTypes.string.isRequired,
        createdAt: PropTypes.string.isRequired,
    }).isRequired,
};

// Export the component
export default InstructionItem;

// Styled Components
const InstructionContainer = styled.div`
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    background-color: #f9f9f9;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease; // Add a transition for a smooth hover effect

    &:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); // Increase shadow on hover
    }
`;

const InstructionHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
`;

const Title = styled.h2`
    font-size: 1.5rem;
    color: #333;
`;

const ToggleButton = styled.button`
    background-color: #61dafb;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    display: flex; // Make the button a flex container
    align-items: center; // Align icon and text vertically
    gap: 5px; // Add a small gap between icon and text

    &:hover {
        background-color: #21a1f1;
    }
`;

const InstructionDetails = styled.div`
    margin-top: 16px;
    font-size: 1rem;
    line-height: 1.5;
`;

const Content = styled.p`
    color: #666;
`;

const MetaInfo = styled.div`
    margin-top: 10px;
    font-size: 0.875rem;
    color: #888;
    span {
        margin-right: 16px;
    }
`;