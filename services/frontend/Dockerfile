# Dockerfile for Vue.js 3 + Vite Frontend
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies first for better caching
COPY package*.json ./

# Clear npm cache and install dependencies with verbose logging
RUN npm cache clean --force && \
    npm install --verbose && \
    npm ls --depth=0

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
