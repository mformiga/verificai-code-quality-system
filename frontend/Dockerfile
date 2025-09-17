# Development stage
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port for Vite dev server
EXPOSE 5173

# Command to start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
