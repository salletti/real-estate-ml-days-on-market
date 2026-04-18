# Stage 1 : Build de l'application React
FROM node:20-alpine AS builder

WORKDIR /app

# Copie des manifestes en premier (cache Docker)
COPY package*.json ./
RUN npm ci

# Variable d'environnement injectée au build
# Vide en local Docker (nginx proxifie /api → backend)
# En production Vercel : VITE_API_BASE_URL=https://your-backend.onrender.com/api/v1
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN npm run build

# Stage 2 : Serveur nginx pour le bundle statique
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
