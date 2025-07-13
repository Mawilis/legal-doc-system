import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { io } from 'socket.io-client';

// Styled Components for better UI
const InstructionsContainer = styled.div`
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  max-width: 800px;
  margin: 20px auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const InstructionItem = styled.div`
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
`;

const InstructionText = styled.p`
  margin: 0;
`;

const AddInstructionForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
`;

const Input = styled.input`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Textarea = styled.textarea`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Button = styled.button`
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
`;

const Instructions = () => {
    const [instructions, setInstructions] = useState([]);
    const [newTitle, setNewTitle] = useState('');
    const [newContent, setNewContent] = useState('');
    const [error, setError] = useState(null);
    const socket = io('http://localhost:3001');  // Adjust to match your backend

    useEffect(() => {
        const fetchInstructions = async () => {
            try {
                const response = await axios.get('/api/instructions');
                setInstructions(response.data);
            } catch (err) {
                console.error('Error fetching instructions:', err);
                setError('Error fetching instructions');
            }
        };

        fetchInstructions();

        // Listen for real-time updates via Socket.io
        socket.on('instruction-added', (newInstruction) => {
            setInstructions((prev) => [newInstruction, ...prev]); // Add new instruction to the top of the list
        });

        return () => {
            socket.disconnect();  // Clean up socket connection on component unmount
        };
    }, [socket]);

    const handleAddInstruction = async (e) => {
        e.preventDefault();
        if (!newTitle || !newContent) {
            setError('Title and content are required');
            return;
        }

        const newInstruction = { title: newTitle, content: newContent };

        try {
            // Post the new instruction to the server
            await axios.post('/api/instructions', newInstruction);

            // Emit event to notify others about the new instruction
            socket.emit('instruction-added', newInstruction);

            // Clear form inputs
            setNewTitle('');
            setNewContent('');
            setError(null);  // Clear any previous errors
        } catch (err) {
            console.error('Error adding instruction:', err);
            setError('Failed to add instruction');
        }
    };

    return (
        <InstructionsContainer>
            <h2>Instructions</h2>

            {error && <ErrorText>{error}</ErrorText>}

            {instructions.length === 0 ? (
                <p>No instructions available</p>
            ) : (
                instructions.map((instruction) => (
                    <InstructionItem key={instruction._id}>
                        <h3>{instruction.title}</h3>
                        <InstructionText>{instruction.content}</InstructionText>
                    </InstructionItem>
                ))
            )}

            <AddInstructionForm onSubmit={handleAddInstruction}>
                <h3>Add New Instruction</h3>
                <Input
                    type="text"
                    placeholder="Instruction Title"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                />
                <Textarea
                    rows="5"
                    placeholder="Instruction Content"
                    value={newContent}
                    onChange={(e) => setNewContent(e.target.value)}
                />
                <Button type="submit">Add Instruction</Button>
            </AddInstructionForm>
        </InstructionsContainer>
    );
};

export default Instructions;
