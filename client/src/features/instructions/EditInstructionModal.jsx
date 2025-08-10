// ~/client/src/components/modals/EditInstructionModal.jsx

import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import Button from '../atoms/Button'; // Use our masterpiece Button

// --- Validation Schema for the Instruction Form ---
const InstructionSchema = Yup.object().shape({
    title: Yup.string().min(3, 'Title is too short').required('Title is required'),
    content: Yup.string().min(10, 'Content must be at least 10 characters').required('Content is required'),
});

// --- Styled Components ---

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ModalBox = styled.div`
  background: ${({ theme }) => theme.colors.background || '#fff'};
  padding: 2rem;
  border-radius: 10px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.h2`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.text || '#333'};
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
`;

const StyledForm = styled(Form)`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

const StyledField = styled(Field)`
  padding: 0.75rem;
  border-radius: 5px;
  border: 1px solid ${({ theme }) => theme.colors.border || '#ccc'};
  font-size: 1rem;
`;

const StyledTextarea = styled(StyledField)`
  resize: vertical;
  min-height: 120px;
`;

const ErrorText = styled(ErrorMessage)`
  color: ${({ theme }) => theme.colors.danger || '#d32f2f'};
  font-size: 0.85rem;
`;

const ButtonRow = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
`;

/**
 * A modal component for editing an instruction.
 * It uses Formik for form handling and Yup for validation.
 *
 * @param {object} props
 * @param {boolean} props.open - Controls if the modal is visible.
 * @param {object} props.instruction - The instruction object to be edited.
 * @param {Function} props.onClose - Function to call when the modal should be closed.
 * @param {Function} props.onSubmit - Function to call with the form values on submission.
 */
const EditInstructionModal = ({ open, instruction, onClose, onSubmit }) => {
    if (!open) return null;

    return (
        <Overlay>
            <ModalBox>
                <ModalHeader>Edit Instruction</ModalHeader>

                <Formik
                    initialValues={{
                        title: instruction?.title || '',
                        content: instruction?.content || '',
                    }}
                    validationSchema={InstructionSchema}
                    onSubmit={(values, actions) => {
                        onSubmit(values);
                        actions.setSubmitting(false);
                    }}
                    enableReinitialize // Ensures the form updates if the instruction prop changes
                >
                    {() => (
                        <StyledForm>
                            <FormGroup>
                                <StyledLabel htmlFor="title">Title</StyledLabel>
                                <StyledField id="title" name="title" />
                                <ErrorText component="div" name="title" />
                            </FormGroup>

                            <FormGroup>
                                <StyledLabel htmlFor="content">Content</StyledLabel>
                                <StyledTextarea id="content" name="content" as="textarea" />
                                <ErrorText component="div" name="content" />
                            </FormGroup>

                            <ButtonRow>
                                <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
                                <Button type="submit" variant="success">Save Changes</Button>
                            </ButtonRow>
                        </StyledForm>
                    )}
                </Formik>
            </ModalBox>
        </Overlay>
    );
};

EditInstructionModal.propTypes = {
    open: PropTypes.bool.isRequired,
    instruction: PropTypes.object,
    onClose: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
};

export default EditInstructionModal;
