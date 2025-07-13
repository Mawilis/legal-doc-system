const bcrypt = require('bcryptjs');

const hashPassword = async (password) => {
    try {
        const salt = await bcrypt.genSalt(12);
        const hashedPassword = await bcrypt.hash(password, salt);
        console.log("Hashed Password:", hashedPassword);
    } catch (error) {
        console.error("Error hashing password:", error);
    }
};

// Change "YourSecurePassword123!" to the password you want to use
hashPassword("Kim@Siya8598");
