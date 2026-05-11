FROM node:22-alpine

WORKDIR /app

# Copy dependency files for layer caching
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the app
COPY . .

EXPOSE 5173

# --host 0.0.0.0 needed so Vite listens on all interfaces inside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
