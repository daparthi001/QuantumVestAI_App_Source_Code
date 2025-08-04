FROM node:18-alpine AS build
WORKDIR /app
COPY ui/package*.json ./
RUN npm install
COPY ui/ .
RUN npm run build && mv dist build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
RUN mkdir -p /usr/share/nginx/html/health \
    && echo '{"status":"healthy"}' > /usr/share/nginx/html/health/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

