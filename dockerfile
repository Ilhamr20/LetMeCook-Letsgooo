# Gunakan Node.js sebagai base image
FROM node:16

# Set working directory di dalam container
WORKDIR /app

# Salin file package.json dan package-lock.json untuk menginstall dependencies
COPY package*.json /app/

# Install dependencies
RUN npm install

# Salin semua file aplikasi ke dalam container
COPY . /app/

# Mengekspos port aplikasi (misalnya 8080 untuk Cloud Run)
EXPOSE 8000

# Jalankan aplikasi Node.js
CMD ["npm", "start"]
