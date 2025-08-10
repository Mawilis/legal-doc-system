
// ~/client/src/features/settings/pages/Tags.jsx

import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 2rem;
`;

const Heading = styled.h2`
  margin-bottom: 1rem;
`;

const TagList = styled.ul`
  margin-top: 1rem;
  list-style: none;
  padding: 0;
`;

const TagItem = styled.li`
  padding: 8px 12px;
  background-color: #e0e0e0;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
`;

const Input = styled.input`
  padding: 8px;
  margin-right: 8px;
  width: 200px;
`;

const Button = styled.button`
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }
`;

const Tags = () => {
    const [tag, setTag] = useState('');
    const [tags, setTags] = useState(['Legal', 'Pending', 'Archived']);

    const handleAddTag = () => {
        if (tag.trim()) {
            setTags((prev) => [...prev, tag]);
            setTag('');
        }
    };

    const handleRemoveTag = (t) => {
        setTags((prev) => prev.filter((item) => item !== t));
    };

    return (
        <Container>
            <Heading>Tag Management</Heading>

            <div>
                <Input
                    type="text"
                    placeholder="Enter new tag"
                    value={tag}
                    onChange={(e) => setTag(e.target.value)}
                />
                <Button onClick={handleAddTag}>Add</Button>
            </div>

            <TagList>
                {tags.map((t) => (
                    <TagItem key={t}>
                        {t}
                        <button onClick={() => handleRemoveTag(t)} style={{ background: 'transparent', border: 'none', color: 'red' }}>
                            ✕
                        </button>
                    </TagItem>
                ))}
            </TagList>
        </Container>
    );
};

export default Tags;