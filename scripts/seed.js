require('dotenv').config();
const mongoose = require('mongoose');
const User = require('../server/models/userModel'); // Adjust this path to match your existing model location

mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

const seedUsers = async () => {
    try {
        await User.deleteMany({});
        await User.create([
            {
                name: 'Admin User',
                email: 'admin@example.com',
                password: 'admin1234',
                role: 'admin'
            },
            {
                name: 'Regular User',
                email: 'user@example.com',
                password: 'user1234',
                role: 'user'
            }
        ]);
        console.log('Database seeded successfully');
        process.exit();
    } catch (err) {
        console.error('Error seeding the database', err);
        process.exit(1);
    }
};

seedUsers();
