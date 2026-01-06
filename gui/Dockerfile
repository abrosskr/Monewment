# Frontend Dockerfile (Dev Mode)
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
# If package-lock.json doesn't exist, npm install will generate one from package.json
RUN npm install

# Copy source code
COPY . .

# Next.js Dev server runs on port 3000
EXPOSE 3000

# Run in development mode for hot-reloading
CMD ["npm", "run", "dev"]
