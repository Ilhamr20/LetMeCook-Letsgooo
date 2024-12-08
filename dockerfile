# Gunakan Node.js sebagai base image
FROM node:16

# Set working directory di dalam container
WORKDIR /app

ENV HOST 0.0.0.0

# Salin file package.json dan package-lock.json untuk menginstall dependencies
COPY package*.json /app/

# Install dependencies
RUN npm install

# Salin semua file aplikasi ke dalam container
COPY . /app/

ENV PORT=3000
ENV PORT=8080

# Mengekspos port aplikasi (misalnya 8080 untuk Cloud Run)
EXPOSE 3000
EXPOSE 8080

# Jalankan aplikasi Node.js
CMD ["npm", "start"]
