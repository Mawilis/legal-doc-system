const sendEmail = require('./sendMail');
const nodemailer = require('nodemailer');
const axios = require('axios');

jest.mock('axios');
jest.mock('nodemailer');

describe('sendEmail()', () => {
    let mockSend;

    beforeEach(() => {
        mockSend = jest.fn().mockResolvedValue({ messageId: '12345' });

        nodemailer.createTransport.mockReturnValue({
            sendMail: mockSend,
        });
    });

    it('sends an email successfully', async () => {
        await sendEmail({
            email: 'test@example.com',
            subject: 'Hello',
            text: 'Test email',
        });

        expect(mockSend).toHaveBeenCalled();
    });

    it('retries failed sends up to 3 times', async () => {
        let count = 0;
        mockSend.mockImplementation(() => {
            count++;
            if (count < 3) throw new Error(`Fail ${count}`);
            return Promise.resolve({ messageId: 'afterRetries' });
        });

        await sendEmail({
            email: 'test@example.com',
            subject: 'Retry Test',
            text: 'Should retry',
        });

        expect(mockSend).toHaveBeenCalledTimes(3);
    });

    it('sends Slack alert if alert flag is set', async () => {
        // ✅ Set environment variable for test run
        process.env.SLACK_ALERT_WEBHOOK = 'https://hooks.slack.com/services/test';

        await sendEmail({
            email: 'test@example.com',
            subject: 'Alert Email',
            text: 'Important',
            alert: true,
        });

        expect(axios.post).toHaveBeenCalledWith(
            expect.any(String),
            expect.objectContaining({ text: expect.stringContaining('Alert Email') })
        );
    });
});
