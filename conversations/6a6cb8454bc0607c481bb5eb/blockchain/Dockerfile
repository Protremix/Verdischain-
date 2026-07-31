FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist/ ./dist/
COPY node_modules/ ./node_modules/
RUN mkdir -p /app/data
ENV PORT=3200
ENV NODE_ENV=production
EXPOSE 3200
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3200/api/blockchain/info || exit 1
CMD ["node", "dist/index.js"]
