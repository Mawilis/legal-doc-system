// src/pages/Profile.jsx

import React, { useState, useEffect } from 'react';
import { getUserDetails, updateUserProfile } from '../services/userService'; // Correct path to userService
import './Profile.css'; // Ensure Profile.css is in the same directory

const Profile = () => {
    const [profile, setProfile] = useState({ name: '', email: '' });
    const [error, setError] = useState(null);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await getUserDetails();
                setProfile(data);
            } catch (err) {
                setError('Error fetching profile');
            }
        };

        fetchProfile();
    }, []);

    const handleUpdate = async () => {
        try {
            await updateUserProfile(profile);
            setIsEditing(false);
        } catch (err) {
            setError('Error updating profile');
        }
    };

    return (
        <div className="profile-container">
            <h1>Profile</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div className="profile-field">
                <label>Name:</label>
                {isEditing ? (
                    <input
                        type="text"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    />
                ) : (
                    <p>{profile.name}</p>
                )}
            </div>
            <div className="profile-field">
                <label>Email:</label>
                {isEditing ? (
                    <input
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    />
                ) : (
                    <p>{profile.email}</p>
                )}
            </div>
            {isEditing ? (
                <button onClick={handleUpdate}>Save</button>
            ) : (
                <button onClick={() => setIsEditing(true)}>Edit Profile</button>
            )}
        </div>
    );
};

export default Profile;
