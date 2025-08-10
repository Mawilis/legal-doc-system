// ~/client/src/components/InstructionItem.jsx

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChevronDown, FaChevronUp, FaEdit, FaTrash } from 'react-icons/fa';
import Button from './atoms/Button';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useDispatch } from 'react-redux';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { updateInstruction, deleteInstruction } from '../features/instructions/reducers/instructionSlice';

// --- Constants ---
const ROLES = ['admin', 'sheriff', 'attorney', 'user']; // Define all available roles

// --- Validation Schema for the Edit Form ---
const InstructionValidationSchema = Yup.object({
    title: Yup.string().min(3, 'Title is too short').required('Title is required'),
    content: Yup.string().min(10, 'Content is too short').required('Content is required'),
    allowedRoles: Yup.array().min(1, 'At least one role must be selected').required('Role selection is required'),
});

// --- Reusable Modal and Form Components ---

const Modal = ({ open, onClose, children }) => {
    if (!open) return null;
    return (
        <ModalOverlay onClick={onClose}>
            <ModalBox onClick={(e) => e.stopPropagation()}>{children}</ModalBox>
        </ModalOverlay>
    );
};

const ConfirmationDialog = ({ open, onClose, onConfirm, title, message }) => (
    <Modal open={open} onClose={onClose}>
        <ModalTitle>{title}</ModalTitle>
        <p>{message}</p>
        <ActionRow>
            <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
            <Button type="button" variant="danger" onClick={onConfirm}>Confirm Delete</Button>
        </ActionRow>
    </Modal>
);

const EditInstructionModal = ({ open, instruction, onClose, onSubmit }) => (
    <Modal open={open} onClose={onClose}>
        <ModalTitle>Edit Instruction</ModalTitle>
        <Formik
            initialValues={{
                title: instruction.title,
                content: instruction.content,
                allowedRoles: instruction.allowedRoles || [], // Initialize with existing roles
            }}
            validationSchema={InstructionValidationSchema}
            onSubmit={onSubmit}
            enableReinitialize
        >
            {({ values, setFieldValue, isSubmitting }) => (
                <StyledForm>
                    <FormGroup>
                        <StyledLabel htmlFor="title">Title</StyledLabel>
                        <Field as={StyledInput} id="title" name="title" placeholder="Instruction Title" />
                        <StyledErrorMessage name="title" component="div" />
                    </FormGroup>
                    <FormGroup>
                        <StyledLabel>Content</StyledLabel>
                        <StyledQuill theme="snow" value={values.content} onChange={(value) => setFieldValue('content', value)} />
                        <StyledErrorMessage name="content" component="div" />
                    </FormGroup>
                    <FormGroup>
                        <StyledLabel>Visible To Roles</StyledLabel>
                        <RoleSelectWrapper>
                            {ROLES.map((role) => (
                                <RoleLabel key={role}>
                                    <input
                                        type="checkbox"
                                        name="allowedRoles"
                                        value={role}
                                        checked={values.allowedRoles.includes(role)}
                                        onChange={(e) => {
                                            const { checked, value } = e.target;
                                            const updatedRoles = checked
                                                ? [...values.allowedRoles, value]
                                                : values.allowedRoles.filter(r => r !== value);
                                            setFieldValue('allowedRoles', updatedRoles);
                                        }}
                                    />
                                    {role}
                                </RoleLabel>
                            ))}
                        </RoleSelectWrapper>
                        <StyledErrorMessage name="allowedRoles" component="div" />
                    </FormGroup>
                    <ActionRow>
                        <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
                        <Button type="submit" variant="success" disabled={isSubmitting}>
                            {isSubmitting ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </ActionRow>
                </StyledForm>
            )}
        </Formik>
    </Modal>
);

/**
 * A collapsible/expandable UI component for displaying, editing, and deleting a single instruction.
 */
const InstructionItem = ({ instruction }) => {
    const dispatch = useDispatch();
    const [isExpanded, setIsExpanded] = useState(false);
    const [isEditModalOpen, setEditModalOpen] = useState(false);
    const [isConfirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

    const toggleDetails = () => setIsExpanded(!isExpanded);

    const handleUpdateInstruction = async (values, { setSubmitting }) => {
        try {
            await dispatch(updateInstruction({ instructionId: instruction._id, ...values })).unwrap();
            setEditModalOpen(false);
        } catch (err) {
            // Error toast is handled by the slice
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async () => {
        try {
            await dispatch(deleteInstruction(instruction._id)).unwrap();
        } catch (err) {
            // Error toast is handled by the slice
        } finally {
            setConfirmDeleteOpen(false);
        }
    };

    return (
        <>
            <InstructionContainer
                layout
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                role="region"
                aria-labelledby={`instruction-${instruction._id}`}
            >
                <InstructionHeader>
                    <Title id={`instruction-${instruction._id}`}>{instruction.title}</Title>
                    <ActionGroup>
                        <Button size="small" ghost onClick={(e) => { e.stopPropagation(); setEditModalOpen(true); }} title="Edit Instruction">
                            <FaEdit />
                        </Button>
                        <Button size="small" ghost variant="danger" onClick={(e) => { e.stopPropagation(); setConfirmDeleteOpen(true); }} title="Delete Instruction">
                            <FaTrash />
                        </Button>
                        <Button size="small" outline onClick={toggleDetails} aria-expanded={isExpanded}>
                            {isExpanded ? <FaChevronUp /> : <FaChevronDown />}
                            <span>{isExpanded ? 'Hide' : 'Details'}</span>
                        </Button>
                    </ActionGroup>
                </InstructionHeader>

                <AnimatePresence>
                    {isExpanded && (
                        <InstructionDetails
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3, ease: 'easeInOut' }}
                        >
                            <Content dangerouslySetInnerHTML={{ __html: instruction.content }} />
                            <MetaInfo>
                                <span>Created by: <strong>{instruction.creator}</strong></span>
                                <span>Date: {new Date(instruction.createdAt).toLocaleDateString()}</span>
                            </MetaInfo>
                        </InstructionDetails>
                    )}
                </AnimatePresence>
            </InstructionContainer>

            {/* --- Modals --- */}
            <EditInstructionModal
                open={isEditModalOpen}
                instruction={instruction}
                onClose={() => setEditModalOpen(false)}
                onSubmit={handleUpdateInstruction}
            />
            <ConfirmationDialog
                open={isConfirmDeleteOpen}
                onClose={() => setConfirmDeleteOpen(false)}
                onConfirm={handleDelete}
                title="Confirm Deletion"
                message={`Are you sure you want to delete the instruction: "${instruction.title}"? This action cannot be undone.`}
            />
        </>
    );
};

InstructionItem.propTypes = {
    instruction: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
        content: PropTypes.string.isRequired,
        creator: PropTypes.string.isRequired,
        createdAt: PropTypes.string.isRequired,
        allowedRoles: PropTypes.arrayOf(PropTypes.string), // Add prop type for roles
    }).isRequired,
};

export default InstructionItem;

// --- Styled Components ---
const InstructionContainer = styled(motion.div)`
  border: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  background-color: ${({ theme }) => theme.colors.background || '#ffffff'};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;
  overflow: hidden;
`;
const InstructionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;
const Title = styled.h2`
  font-size: 1.4rem;
  color: ${({ theme }) => theme.colors.text || '#333'};
  margin: 0;
`;
const InstructionDetails = styled(motion.div)`
  margin-top: 1.5rem;
  font-size: 1rem;
  line-height: 1.6;
  border-top: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  padding-top: 1.5rem;
`;
const Content = styled.div`
  color: ${({ theme }) => theme.colors.textSecondary || '#555'};
  margin: 0 0 1rem 0;
`;
const MetaInfo = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
`;
const ActionGroup = styled.div`
  display: flex;
  gap: 0.5rem;
`;
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
`;
const ModalBox = styled.div`
  background: #fff; padding: 2rem; width: 100%; max-width: 600px;
  border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
`;
const ModalTitle = styled.h3`
  font-size: 1.5rem; color: #333; margin-top: 0; margin-bottom: 1.5rem; text-align: center;
`;
const StyledForm = styled(Form)`
  display: flex; flex-direction: column; gap: 1rem;
`;
const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;
const StyledLabel = styled.label`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.textSecondary || '#555'};
`;
const StyledInput = styled(Field)`
  width: 100%; padding: 0.75rem; border: 1px solid #ccc;
  border-radius: 4px; font-size: 1rem;
`;
const StyledQuill = styled(ReactQuill)`
  .ql-editor {
    min-height: 150px;
  }
`;
const StyledErrorMessage = styled(ErrorMessage)`
  color: #dc3545; font-size: 0.875rem;
`;
const ActionRow = styled.div`
  display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1rem;
`;
const RoleSelectWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
`;
const RoleLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  text-transform: capitalize;
`;
