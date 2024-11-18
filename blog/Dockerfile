# Stage 1: Build the React app
FROM node:16-alpine AS build

WORKDIR /app

# Copy necessary files and install dependencies
COPY package.json yarn.lock .eslintrc.json ./
RUN yarn install --frozen-lockfile

# Copy the rest of the application code and build
COPY . ./
RUN yarn build

# Stage 2: Serve the React app using Nginx
FROM nginx:stable-alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d

# Copy the built React app from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]