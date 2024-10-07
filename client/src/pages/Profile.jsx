// Profile.jsx
import React, { useState, useEffect } from 'react';
import { getProfile, updateProfile } from '../services/userService';

const Profile = () => {
    const [profile, setProfile] = useState({ name: '', email: '' });
    const [error, setError] = useState(null);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await getProfile();
                setProfile(data);
            } catch (err) {
                setError('Error fetching profile');
            }
        };

        fetchProfile();
    }, []);

    const handleUpdate = async () => {
        try {
            await updateProfile(profile);
            setIsEditing(false);
        } catch (err) {
            setError('Error updating profile');
        }
    };

    return (
        <div>
            <h1>Profile</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div>
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
            <div>
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
