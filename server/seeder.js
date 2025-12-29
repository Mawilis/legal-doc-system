const mongoose = require('mongoose');
const dotenv = require('dotenv');
const colors = require('colors');
// Import your Status model if you created one, otherwise this step is for reference
// const Status = require('./models/statusModel'); 

dotenv.config();

const seedStatuses = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGO_URI);
        console.log(`MongoDB Connected: ${conn.connection.host}`.cyan.underline);

        // If you have a separate Status collection:
        // await Status.deleteMany();
        // await Status.insertMany([
        //   { name: "Draft", description: "Document created, editable by staff" },
        //   { name: "Pending", description: "Awaiting approval or assignment" },
        //   // ... add all others
        // ]);

        console.log('Statuses Imported!'.green.inverse);
        process.exit();
    } catch (error) {
        console.error(`${error}`.red.inverse);
        process.exit(1);
    }
};

seedStatuses();