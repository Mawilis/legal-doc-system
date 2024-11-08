// ~/legal-doc-system/client/src/features/profile/pages/Profile.jsx

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUserProfile, updateUserProfile } from '../reducers/profileSlice';
import { FaSave } from 'react-icons/fa';

const ProfileContainer = styled.div`
  padding: var(--spacing-lg);
  background-color: var(--background-color);
  min-height: 100vh;
`;

const ProfileHeader = styled.div`
  margin-bottom: var(--spacing-md);
`;

const ProfileTitle = styled.h1`
  font-size: 2.5rem;
  color: var(--primary-color);
`;

const ProfileForm = styled.form`
  display: flex;
  flex-direction: column;
  max-width: 500px;
`;

const FormGroup = styled.div`
  margin-bottom: var(--spacing-sm);
`;

const Label = styled.label`
  margin-bottom: 0.5rem;
  color: var(--text-color);
`;

const Input = styled.input`
  padding: var(--spacing-sm);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
`;

const TextArea = styled.textarea`
  padding: var(--spacing-sm);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
  resize: vertical;
`;

const SaveButton = styled.button`
  display: flex;
  align-items: center;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color var(--transition);
  margin-top: var(--spacing-md);

  &:hover {
    background-color: var(--secondary-color);
  }

  svg {
    margin-left: 0.5rem;
  }
`;

const Loading = styled.div`
  text-align: center;
  font-size: 1.5rem;
  color: var(--primary-color);
`;

const ErrorMessage = styled.p`
  color: var(--error-color);
  text-align: center;
  font-size: 1.2rem;
`;

const Profile = () => {
  const dispatch = useDispatch();
  const { userProfile, loading, error } = useSelector((state) => state.profile);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: '',
  });

  useEffect(() => {
    dispatch(fetchUserProfile());
  }, [dispatch]);

  useEffect(() => {
    if (userProfile) {
      setFormData({
        name: userProfile.name || '',
        email: userProfile.email || '',
        bio: userProfile.bio || '',
      });
    }
  }, [userProfile]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(updateUserProfile(formData));
  };

  if (loading) {
    return <Loading>Loading Profile...</Loading>;
  }

  if (error) {
    return <ErrorMessage>{error}</ErrorMessage>;
  }

  return (
    <ProfileContainer>
      <ProfileHeader>
        <ProfileTitle>My Profile</ProfileTitle>
      </ProfileHeader>
      <ProfileForm onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="name">Name</Label>
          <Input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </FormGroup>
        <FormGroup>
          <Label htmlFor="email">Email</Label>
          <Input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </FormGroup>
        <FormGroup>
          <Label htmlFor="bio">Bio</Label>
          <TextArea
            id="bio"
            name="bio"
            rows="4"
            value={formData.bio}
            onChange={handleChange}
          />
        </FormGroup>
        <SaveButton type="submit">
          Save Changes <FaSave />
        </SaveButton>
      </ProfileForm>
    </ProfileContainer>
  );
};

export default Profile;
