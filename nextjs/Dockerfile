# Use an official Node.js runtime as a parent image
FROM node:20.12.0-alpine

# Set the working directory in the container
WORKDIR /app

# Install yarn if not already installed
RUN apk add --no-cache yarn

# Copy package.json and yarn.lock (if exists)
COPY package*.json yarn.lock* ./

# Install project dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN yarn build

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the app in development mode
CMD ["yarn", "dev"] 