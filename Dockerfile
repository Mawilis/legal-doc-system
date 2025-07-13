# Use the official Node.js 14 image as a base
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy all the project files into the container
COPY . .

# Expose port 3001 to be used by the container
EXPOSE 3001

# Command to start the server
CMD ["npm", "start"]
