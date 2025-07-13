import React from 'react';
import styled from 'styled-components';

const JobCard = ({ job }) => {
    return (
        <Card>
            <h3>{job.title}</h3>
            <p>{job.description}</p>
            <Button>Apply Now</Button>
        </Card>
    );
};

export default JobCard;

const Card = styled.div`
  border: 1px solid #ddd;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  background: #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const Button = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
  }
`;
