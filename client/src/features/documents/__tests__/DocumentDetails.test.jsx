import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import DocumentDetails from '../pages/DocumentDetails';
import { store } from '../../../store';

test('renders document details correctly', async () => {
    render(
        <Provider store={store}>
            <BrowserRouter>
                <DocumentDetails />
            </BrowserRouter>
        </Provider>
    );

    expect(screen.getByText('Loading document details...')).toBeInTheDocument();
});

test('shows mark as scanned button', async () => {
    render(
        <Provider store={store}>
            <BrowserRouter>
                <DocumentDetails />
            </BrowserRouter>
        </Provider>
    );

    expect(screen.getByText('Mark as Scanned')).toBeInTheDocument();
});
