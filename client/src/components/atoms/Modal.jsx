import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: ${({ show }) => (show ? 'flex' : 'none')};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalBox = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  min-width: 300px;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.2);
`;

const Modal = ({ show, onClose, children }) => {
    return (
        <Overlay show={show} onClick={onClose}>
            <ModalBox onClick={(e) => e.stopPropagation()}>
                {children}
            </ModalBox>
        </Overlay>
    );
};

Modal.propTypes = {
    show: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    children: PropTypes.node,
};

export default Modal;
