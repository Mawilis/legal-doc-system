// utils/sendEmail.js

const nodemailer = require('nodemailer');

// Configure and send email using Nodemailer
const sendEmail = async (options) => {
    // Create a transporter object using SMTP
    const transporter = nodemailer.createTransport({
        host: process.env.EMAIL_HOST || 'smtp.gmail.com', // Email service host
        port: process.env.EMAIL_PORT || 587, // SMTP port (587 for TLS)
        secure: false, // Set to true for port 465, false for other ports
        auth: {
            user: process.env.EMAIL_USERNAME, // Email username
            pass: process.env.EMAIL_PASSWORD, // Email password or app-specific password
        },
    });

    // Define email options
    const mailOptions = {
        from: 'Your App Name <no-reply@yourapp.com>', // Sender's email address
        to: options.email, // Recipient's email address
        subject: options.subject, // Subject line
        text: options.message, // Plain text message
        html: options.html || undefined, // Optional HTML version of the message
    };

    // Send the email
    await transporter.sendMail(mailOptions);
};

module.exports = sendEmail;
