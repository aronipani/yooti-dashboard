FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

EXPOSE 5173

# Vite dev server — binds to 0.0.0.0 so Docker can expose the port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
