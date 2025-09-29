import express from "express";
import pkg from "pg";
import dotenv from "dotenv";

dotenv.config();
const { Pool } = pkg;

const app = express();
app.use(express.json());
const port = process.env.PORT || 3000;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: false, 
});

function formatMedicos(rows) {
  return rows.map((m, i) => `${i + 1}. ${m.nombre} (DNI: ${m.dni})`).join("\n");
}

app.all("/medicos", async (req, res) => {
  try {
    const result = await pool.query("SELECT id_medico, nombre, dni FROM medicos");
    const texto = formatMedicos(result.rows);

    res.json({
      status: "ok",
      mensaje: texto,
      medicos: result.rows,
    });
  } catch (error) {
    console.error("Error al obtener médicos:", error);
    res.status(500).json({ status: "error", message: "Error interno del servidor" });
  }
});

app.listen(port, () => {
  console.log(`Servidor corriendo en http://localhost:${port}`);
});
