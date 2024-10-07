import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components'; // Import styled-components for styling

// DocumentCard component
const DocumentCard = ({ document }) => {
    return (
        <CardContainer>
            <Title>{document.title}</Title>
            <Metadata>
                <Author>Created by: {document.author || 'Unknown Author'}</Author>
                <Date>{new Date(document.createdAt).toLocaleDateString()}</Date>
            </Metadata>
            <Content>{document.content}</Content>
            <Actions>
                <Button>View</Button>
                <Button>Edit</Button>
            </Actions>
        </CardContainer>
    );
};

// Define prop types for better validation
DocumentCard.propTypes = {
    document: PropTypes.shape({
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
`;

const Title = styled.h2`
    font-size: 24px;
    margin-bottom: 10px;
    color: #333;
`;

const Metadata = styled.div`
    font-size: 14px;
    color: #777;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
`;

const Author = styled.span``;

const Date = styled.span``;

const Content = styled.p`
    font-size: 16px;
    line-height: 1.5;
    color: #555;
`;

const Actions = styled.div`
    display: flex;
    gap: 10px;
    margin-top: 15px;
`;

const Button = styled.button`
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    background-color: #4caf50;
    color: white;
    cursor: pointer;
    font-size: 14px;

    &:hover {
        background-color: #45a049;
    }
`;
