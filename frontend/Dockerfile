# Development image: runs the Vite dev server with hot reload.
# A production build (nginx serving static files) comes in the deployment phase.
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
