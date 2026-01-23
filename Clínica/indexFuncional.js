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

function cleanString(str) {
  return str.replace(/[\u200B-\u200D\uFEFF]/g, "");
}

app.all("/medicos", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT id_medico, nombre, dni FROM medicos"
    );
    const texto = cleanString(formatMedicos(result.rows));

    res.json({
      status: "ok",
      mensaje: texto,
      medicos: result.rows.map((m) => ({
        id_medico: cleanString(m.id_medico.toString()),
        nombre: cleanString(m.nombre),
        dni: cleanString(m.dni),
      })),
    });
  } catch (error) {
    console.error("Error al obtener médicos:", error);
    res
      .status(500)
      .json({ status: "error", message: "Error interno del servidor" });
  }
});

app.listen(port, () => {
  console.log(`Servidor corriendo en http://localhost:${port}`);
});
