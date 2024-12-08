const express = require("express");
const dotenv = require("dotenv");
const sequelize = require("./config/database.js");
const router = require("./routes/index.js");
const mlRoutes = require("./routes/mlService.js"); // Mengimpor mlRoutes
const {
  setupBahanResepAssociations,
  setupKategoriResepAssociations,
} = require("./models/index.js");
const app = express();

dotenv.config();

// Middleware untuk JSON parsing
app.use(express.json());

// Menggunakan router utama dan service router (untuk ML)
app.use(router);
app.use("/api/ml", mlRoutes); // Menambahkan rute ML

// Menyiapkan asosiasi untuk model
setupBahanResepAssociations();
setupKategoriResepAssociations();

// Menghubungkan ke database dan mensinkronkan model
sequelize
  .authenticate() // Mengecek koneksi database
  .then(() => {
    console.log("Database connected successfully");

    // Sync database setelah koneksi berhasil
    sequelize
      .sync({ force: false }) // Ganti dengan { alter: true } jika ingin update tanpa menghapus data
      .then(() => {
        console.log("Database synced successfully");
      })
      .catch((syncError) => {
        console.error("Error syncing database:", syncError);
      });
  })
  .catch((error) => {
    console.error("Database connection failed:", error);
  });

// Menjalankan server
const PORT = process.env.APP_PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
