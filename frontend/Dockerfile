# Base image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
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
