# Build stage
FROM --platform=linux/amd64 node:18.17.0 AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with specific platform
ENV ROLLUP_SKIP_NODEJS_CHECKS=true
RUN npm install --platform=linux --arch=x64 --no-optional

# Copy source files
COPY . .

# Build the app with environment variable to skip native dependencies
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Production stage
FROM --platform=linux/amd64 nginx:stable-alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3001

CMD ["nginx", "-g", "daemon off;"]
