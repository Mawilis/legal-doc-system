// ~/legal-doc-system/client/src/features/client/pages/ClientManagement.jsx

import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addClient, updateClient } from '../reducers/clientSlice';
import { Button, TextField } from '@mui/material';

const ClientManagement = () => {
    const dispatch = useDispatch();
    const { clients } = useSelector((state) => state.client);

    useEffect(() => {
        // Logic to fetch clients if needed
    }, [dispatch]);

    const handleAddClient = () => {
        const newClient = {
            id: clients.length + 1,
            name: 'New Client',
            email: 'newclient@example.com',
        };
        dispatch(addClient(newClient));
    };

    return (
        <div>
            <h1>Client Management</h1>
            {clients.map((client) => (
                <div key={client.id}>
                    <h2>{client.name}</h2>
                    <p>{client.email}</p>
                    <Button variant="contained" onClick={() => dispatch(updateClient({ ...client, name: 'Updated Name' }))}>
                        Update Client
                    </Button>
                </div>
            ))}
            <TextField label="Client Name" variant="outlined" />
            <Button variant="contained" onClick={handleAddClient}>
                Add Client
            </Button>
        </div>
    );
};

export default ClientManagement;
