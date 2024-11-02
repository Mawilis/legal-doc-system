const cron = require('node-cron');
const sendEmail = require('../utils/sendEmail');

// Run a task every Monday at 9:00 AM
cron.schedule('0 9 * * 1', async () => {
    console.log('Running weekly email reminder job...');
    try {
        await sendEmail({
            email: 'user@example.com',
            subject: 'Weekly Reminder',
            message: 'This is your weekly reminder!'
        });
        console.log('Reminder email sent successfully.');
    } catch (error) {
        console.error('Error sending reminder email:', error);
    }
});
