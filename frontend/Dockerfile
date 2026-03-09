# Base image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /backend
# Note: Using /backend name because that's what user requested for the backend container.
# Wait, for the frontend container, should it also be /backend?
# The user said "change the docker version of the backend app's name from 'app' to 'backend', so that it matches the local dir name as well".
# So for the frontend container, it should probably be /frontend.

WORKDIR /frontend
COPY package.json package-lock.json* ./
RUN npm install

# Development stage
FROM base AS dev
WORKDIR /frontend
COPY --from=deps /frontend/node_modules ./node_modules
COPY . .

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "run", "dev"]
