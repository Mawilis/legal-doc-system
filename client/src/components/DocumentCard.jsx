import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Link } from 'react-router-dom'; // Import Link for navigation

// DocumentCard component
const DocumentCard = ({ document }) => {
    return (
        <CardContainer>
            <Title>{document.title}</Title> {/* Display document title */}
            <Metadata>
                <Author>Created by: {document.author || 'Unknown Author'}</Author> {/* Display author or "Unknown Author" */}
                <Date>{new Date(document.createdAt).toLocaleDateString()}</Date> {/* Format and display creation date */}
            </Metadata>
            <Content>{document.content}</Content> {/* Display document content */}
            <Actions>
                <Link to={`/documents/${document._id}`}> {/* Link to view document details */}
                    <Button>View</Button>
                </Link>
                <Link to={`/documents/${document._id}/edit`}> {/* Link to edit document */}
                    <Button>Edit</Button>
                </Link>
            </Actions>
        </CardContainer>
    );
};

// Define prop types for validation
DocumentCard.propTypes = {
    document: PropTypes.shape({
        _id: PropTypes.string.isRequired, // Add _id for linking
        title: PropTypes.string.isRequired,
        content: PropTypes.string.isRequired,
        author: PropTypes.string,
        createdAt: PropTypes.string.isRequired,
    }).isRequired,
};

export default DocumentCard;

// Styled Components
const CardContainer = styled.div`
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    background-color: #f9f9f9;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease; /* Add transitions */

    &:hover {
        transform: translateY(-2px); /* Add hover effect */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }
`;

const Title = styled.h2`
    font-size: 1.8em; 
    margin-bottom: 10px;
    color: #333;
`;

const Metadata = styled.div`
    font-size: 0.9em; 
    color: #777;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
`;

const Author = styled.span`
    font-style: italic; 
`;

const Date = styled.span`
    font-style: italic; 
`;

const Content = styled.p`
    font-size: 1em; 
    line-height: 1.5;
    color: #555;
`;

const Actions = styled.div`
    display: flex;
    gap: 10px; 
    margin-top: 15px;
`;

const Button = styled.button`
    padding: 8px 12px; 
    border: none;
    border-radius: 5px;
    background-color: #007bff; 
    color: white;
    cursor: pointer;
    font-size: 0.9em; 
    transition: background-color 0.2s ease; 

    &:hover {
        background-color: #0062cc; 
    }
`;