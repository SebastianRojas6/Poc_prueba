import express from "express";
import pkg from "pg";
import dotenv from "dotenv";

dotenv.config();
const { Pool } = pkg;

const app = express();
app.use(express.json());
const port = process.env.PORT || 3000;

console.log("Iniciando servidor...");
console.log(
  "DATABASE_URL configurado:",
  process.env.DATABASE_URL ? "✅ SÍ" : "❌ NO"
);

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

pool
  .query("SELECT NOW()")
  .then(() => console.log("✅ Conexión a Supabase exitosa"))
  .catch((err) =>
    console.error("❌ Error conectando a Supabase:", err.message)
  );

function formatMedicos(rows) {
  return rows.map((m, i) => `${i + 1}. ${m.nombre} (DNI: ${m.dni})`).join("\n");
}

function cleanString(str) {
  return str.replace(/[\u200B-\u200D\uFEFF]/g, "");
}

function generarCodigoCita() {
  const fecha = new Date();
  const dia = String(fecha.getDate()).padStart(2, "0");
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const anio = fecha.getFullYear();
  const random = Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, "0");
  return `C-${random}-${dia}${mes}${anio}`;
}

app.all("/medicos", async (req, res) => {
  console.log("\n====== NUEVA PETICIÓN /medicos ======");
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📥 Método:", req.method);

  try {
    console.log("🔍 Ejecutando query a base de datos...");

    const result = await pool.query(
      "SELECT id_medico, nombre, dni FROM medicos"
    );

    console.log("✅ Query exitosa");
    console.log("📊 Registros obtenidos:", result.rows.length);

    const texto = cleanString(formatMedicos(result.rows));

    const response = {
      status: "ok",
      mensaje: texto,
      medicos: result.rows.map((m) => ({
        id_medico: cleanString(m.id_medico.toString()),
        nombre: cleanString(m.nombre),
        dni: cleanString(m.dni),
      })),
    };

    console.log("📤 Enviando respuesta:");
    console.log(JSON.stringify(response, null, 2));
    console.log("====== FIN PETICIÓN EXITOSA ======\n");

    res.json(response);
  } catch (error) {
    console.error("❌❌❌ ERROR CAPTURADO ❌❌❌");
    console.error("Tipo de error:", error.name);
    console.error("Mensaje:", error.message);
    console.error("Stack:", error.stack);
    console.error("====== FIN PETICIÓN CON ERROR ======\n");

    res.status(500).json({
      status: "error",
      message: "Error interno del servidor",
      detail: error.message,
    });
  }
});

app.get("/medicos/:id_medico/horarios", async (req, res) => {
  console.log(
    "\n====== NUEVA PETICIÓN GET /medicos/:id_medico/horarios ======"
  );
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📋 Params:", req.params);
  console.log("📋 Query:", req.query);

  try {
    const { id_medico } = req.params;
    const { dia } = req.query; // ?dia=Lunes

    console.log("👨‍⚕️ ID Médico:", id_medico);
    console.log("📅 Día:", dia);

    if (!id_medico) {
      return res.json({
        status: "error",
        mensaje: "❌ ID de médico no especificado.",
      });
    }

    if (!dia) {
      return res.json({
        status: "error",
        mensaje: "❌ Día no especificado.",
      });
    }

    // Verificar que el médico existe
    const medicoResult = await pool.query(
      "SELECT id_medico, nombre FROM medicos WHERE id_medico = $1",
      [id_medico]
    );

    if (medicoResult.rows.length === 0) {
      return res.json({
        status: "error",
        mensaje: "❌ Médico no encontrado.",
      });
    }

    const medico = medicoResult.rows[0];
    console.log("✅ Médico encontrado:", medico.nombre);

    // Obtener horarios del médico para ese día
    console.log("🔍 Consultando horarios...");
    const horariosResult = await pool.query(
      `SELECT hora 
       FROM horarios_medicos 
       WHERE id_medico = $1 AND dia_semana = $2 
       ORDER BY hora ASC`,
      [id_medico, dia]
    );

    if (horariosResult.rows.length === 0) {
      return res.json({
        status: "ok",
        mensaje: `El Dr. ${medico.nombre} no tiene horarios configurados para ${dia}.`,
        medico: medico.nombre,
        horarios: [],
      });
    }

    console.log(`✅ Horarios encontrados: ${horariosResult.rows.length}`);

    // Formatear horarios
    const formatearHora = (hora) => {
      const [hh, mm] = hora.split(":");
      const horaNum = parseInt(hh);
      const periodo = horaNum >= 12 ? "pm" : "am";
      const hora12 = horaNum > 12 ? horaNum - 12 : horaNum === 0 ? 12 : horaNum;
      return `${String(hora12).padStart(2, "0")}:${mm} ${periodo}`;
    };

    const horarios = horariosResult.rows.map((row, index) => ({
      numero: index + 1,
      hora: row.hora,
      hora_formateada: formatearHora(row.hora),
    }));

    const listaHorarios = horarios
      .map((h) => `${h.numero}. ${h.hora_formateada}`)
      .join("\n");

    const mensaje = `⏰ Horarios disponibles del Dr. ${medico.nombre} para ${dia}:\n\n${listaHorarios}\n\nResponde con el número del horario que prefieres.`;

    const response = {
      status: "ok",
      mensaje: mensaje,
      medico: medico.nombre,
      dia: dia,
      horarios: horarios,
    };

    console.log("📤 Enviando respuesta:");
    console.log(JSON.stringify(response, null, 2));
    console.log("====== FIN PETICIÓN EXITOSA ======\n");

    res.json(response);
  } catch (error) {
    console.error("❌❌❌ ERROR CAPTURADO ❌❌❌");
    console.error("Tipo de error:", error.name);
    console.error("Mensaje:", error.message);
    console.error("Stack:", error.stack);
    console.error("====== FIN PETICIÓN CON ERROR ======\n");

    res.status(500).json({
      status: "error",
      mensaje: "❌ Ocurrió un error al consultar los horarios.",
    });
  }
});

app.all("/validar-dia", async (req, res) => {
  console.log("\n====== NUEVA PETICIÓN /validar-dia ======");
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📥 Método:", req.method);
  console.log("📋 Body recibido:", JSON.stringify(req.body, null, 2));

  try {
    const body = req.body?.[0];

    let diaEscrito = body?.info?.message?.channel_data?.message?.text?.body;

    if (!diaEscrito || diaEscrito.includes("{{")) {
      diaEscrito = body?.contact?.last_message;
    }

    if (diaEscrito) {
      diaEscrito = diaEscrito.trim();
    }

    console.log("📅 Día escrito por usuario:", diaEscrito);

    const id_medico = body?.contact?.variables?.MEDICO_PRUEBA;
    console.log("👨‍⚕️ ID Médico:", id_medico);

    if (!diaEscrito) {
      return res.json({
        mensaje:
          "❌ Por favor, escribe el día de la semana (Lunes, Martes, Miércoles, Jueves, Viernes, Sábado).",
      });
    }

    if (!id_medico) {
      return res.json({
        mensaje: "❌ No se ha seleccionado un médico.",
      });
    }

    const diaNormalizado =
      diaEscrito.charAt(0).toUpperCase() + diaEscrito.slice(1).toLowerCase();

    const diasValidos = [
      "Lunes",
      "Martes",
      "Miércoles",
      "Jueves",
      "Viernes",
      "Sábado",
    ];

    if (!diasValidos.includes(diaNormalizado)) {
      return res.json({
        mensaje: `❌ "${diaEscrito}" no es un día válido.\n\nPor favor escribe: Lunes, Martes, Miércoles, Jueves, Viernes, Sábado o Domingo.`,
      });
    }

    console.log("🔍 Verificando si el médico atiende ese día...");
    const verificarDia = await pool.query(
      `SELECT COUNT(*) as count 
       FROM horarios_medicos 
       WHERE id_medico = $1 AND dia_semana = $2`,
      [id_medico, diaNormalizado]
    );

    if (verificarDia.rows[0].count == 0) {
      return res.json({
        mensaje: `❌ El médico no atiende los días ${diaNormalizado}.\n\nPor favor, elige otro día.`,
      });
    }

    console.log("✅ Día válido y médico atiende ese día");

    const response = {
      mensaje: `✅ Perfecto, elegiste ${diaNormalizado}.\n\nAhora te mostraré los horarios disponibles.`,
      dia_validado: diaNormalizado,
    };

    console.log("📤 Enviando respuesta:");
    console.log(JSON.stringify(response, null, 2));
    console.log("====== FIN PETICIÓN EXITOSA ======\n");

    res.json(response);
  } catch (error) {
    console.error("❌❌❌ ERROR CAPTURADO ❌❌❌");
    console.error("Tipo de error:", error.name);
    console.error("Mensaje:", error.message);
    console.error("Stack:", error.stack);
    console.error("====== FIN PETICIÓN CON ERROR ======\n");

    res.status(500).json({
      mensaje: "❌ Ocurrió un error. Por favor, intenta nuevamente.",
    });
  }
});


app.post("/crear-cita", async (req, res) => {
  console.log("\n====== PETICIÓN POST /crear-cita ======");
  console.log("📥 Body recibido:", JSON.stringify(req.body, null, 2));

  try {
    const body = Array.isArray(req.body) ? req.body[0] : req.body;

    const Horarios_poc = body?.contact?.variables?.["Horarios-poc"] ?? body?.Horarios_poc ?? body?.horarios_poc;
    const MEDICO_PRUEBA = body?.contact?.variables?.MEDICO_PRUEBA ?? body?.MEDICO_PRUEBA;
    const HORARIO_CITA = body?.contact?.variables?.["HORARIO-CITA"] ?? body?.HORARIO_CITA;
    let telefono = body?.contact?.phone ?? body?.telefono ?? body?.phone ?? body?.info?.message?.channel_data?.message?.from ?? body?.last_message_data?.message?.from;

    if (!Horarios_poc || !MEDICO_PRUEBA || !HORARIO_CITA || !telefono) {
      return res.status(400).json({
        mensaje: "❌ Faltan datos requeridos: Horarios_poc, MEDICO_PRUEBA, HORARIO_CITA o teléfono."
      });
    }

    const telefonoRawDigits = String(telefono).replace(/\D/g, "");

    const pacienteResult = await pool.query(
      `SELECT id_paciente, nombre, dni, celular
       FROM pacientes
       WHERE regexp_replace(celular, '\\D', '', 'g') = $1
       LIMIT 1`,
      [telefonoRawDigits]
    );

    if (pacienteResult.rows.length === 0) {
      return res.status(404).json({
        mensaje: `❌ No se encontró un paciente con el número ${telefono}.`
      });
    }

    const paciente = pacienteResult.rows[0];

    const medicoResult = await pool.query(
      "SELECT id_medico, nombre FROM medicos WHERE id_medico = $1",
      [MEDICO_PRUEBA]
    );

    if (medicoResult.rows.length === 0) {
      return res.status(404).json({ mensaje: "❌ Médico no encontrado." });
    }

    const medico = medicoResult.rows[0];

    const horariosResult = await pool.query(
      `SELECT id_horario, hora
       FROM horarios_medicos
       WHERE id_medico = $1 AND dia_semana = $2
       ORDER BY hora ASC`,
      [MEDICO_PRUEBA, Horarios_poc]
    );

    if (horariosResult.rows.length === 0) {
      return res.status(404).json({
        mensaje: `❌ El Dr. ${medico.nombre} no tiene horarios disponibles para ${Horarios_poc}.`
      });
    }

    const indice = parseInt(HORARIO_CITA, 10) - 1;
    if (isNaN(indice) || indice < 0 || indice >= horariosResult.rows.length) {
      return res.status(400).json({
        mensaje: `❌ El número de horario es inválido. Debe estar entre 1 y ${horariosResult.rows.length}.`
      });
    }

    const horaSeleccionada = horariosResult.rows[indice].hora;

    const fechaHoy = new Date().toISOString().slice(0, 10);

    const existeCita = await pool.query(
      `SELECT id_cita FROM citas
       WHERE id_medico = $1 AND fecha = $2 AND hora = $3 AND estado != 'Anulado'`,
      [MEDICO_PRUEBA, fechaHoy, horaSeleccionada]
    );

    if (existeCita.rows.length > 0) {
      return res.status(409).json({ mensaje: "❌ Ese horario ya fue reservado. Elige otro." });
    }

    const consultaResult = await pool.query("SELECT id_consulta FROM consultas LIMIT 1");
    if (consultaResult.rows.length === 0) {
      return res.status(500).json({ mensaje: "❌ No hay consultas registradas en la base de datos." });
    }

    const id_consulta = consultaResult.rows[0].id_consulta;

    const codigo = generarCodigoCita();

    const insert = await pool.query(
      `INSERT INTO citas (codigo, id_paciente, id_medico, id_consulta, fecha, hora, estado)
       VALUES ($1, $2, $3, $4, $5, $6, 'Pendiente')
       RETURNING *`,
      [codigo, paciente.id_paciente, MEDICO_PRUEBA, id_consulta, fechaHoy, horaSeleccionada]
    );

    const cita = insert.rows[0];

    res.json({
      mensaje: "✅ Cita creada correctamente.",
      cita: {
        codigo: cita.codigo,
        paciente: paciente.nombre,
        medico: medico.nombre,
        dia: Horarios_poc,
        hora: horaSeleccionada,
        estado: cita.estado
      }
    });

    console.log("✅ Cita registrada correctamente:", cita);
  } catch (error) {
    console.error("❌ Error en /crear-cita:", error);
    res.status(500).json({ mensaje: "❌ Error interno al crear la cita." });
  }
});

app.all("/verificar-dni", async (req, res) => {
  console.log("\n====== NUEVA PETICIÓN /verificar-dni ======");
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📥 Método:", req.method);
  console.log("📋 Body recibido:", JSON.stringify(req.body, null, 2));

  try {
    const body = req.body?.[0];

    let telefono = body?.contact?.phone;

    if (telefono === "{{phone}}" || !telefono || telefono.includes("{{")) {
      telefono =
        body?.info?.message?.channel_data?.message?.from ||
        body?.last_message_data?.message?.from ||
        body?.contact?.last_message_data?.message?.from;
    }

    let dni = body?.info?.message?.channel_data?.message?.text?.body;

    if (!dni || dni.includes("{{") || dni.trim().length < 8) {
      dni =
        body?.contact?.last_message ||
        body?.last_message_data?.message?.text?.body ||
        body?.contact?.variables?.DNI_USUARIO;
    }

    if (dni) {
      dni = dni
        .trim()
        .replace(/\{\{.*?\}\}/g, "")
        .trim();
    }

    console.log("📞 Teléfono extraído:", telefono);
    console.log("🆔 DNI extraído:", dni);
    console.log("🔍 DNI después de limpiar:", dni);

    if (!dni || dni.length < 8) {
      console.log("❌ DNI no válido o no encontrado");
      return res.json({
        mensaje: "❌ Por favor, ingresa un DNI válido de 8 dígitos.",
      });
    }

    if (!telefono) {
      console.log("❌ No se encontró teléfono en la petición");
      return res.json({
        mensaje: "❌ No se pudo identificar tu número de teléfono.",
      });
    }

    dni = dni.replace(/\D/g, "");

    if (dni.length !== 8) {
      console.log("❌ DNI no tiene 8 dígitos:", dni.length);
      return res.json({
        mensaje: `❌ El DNI debe tener exactamente 8 dígitos. Recibimos: ${dni.length} dígitos.`,
      });
    }

    console.log("🔍 Consultando API de Quertium para DNI:", dni);

    const quertiumResponse = await fetch(
      `https://quertium.com/api/v1/reniec/dni/${dni}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${process.env.QUERTIUM_API_KEY}`,
        },
      }
    );

    if (!quertiumResponse.ok) {
      console.log("❌ Error en API de Quertium:", quertiumResponse.status);
      const errorText = await quertiumResponse.text();
      console.log("Error detallado:", errorText);
      return res.json({
        mensaje:
          "❌ No pudimos verificar tu DNI. Por favor, verifica que sea correcto.",
      });
    }

    const quertiumData = await quertiumResponse.json();
    console.log("✅ Datos de Quertium:", quertiumData);

    const nombreCompleto = [
      quertiumData.primerNombre,
      quertiumData.segundoNombre,
      quertiumData.apellidoPaterno,
      quertiumData.apellidoMaterno,
    ]
      .filter(Boolean)
      .join(" ");

    console.log("👤 Nombre completo:", nombreCompleto);

    const telefonoStr = String(telefono).replace(/^51/, "");

    console.log("🔍 Verificando si paciente existe en BD con DNI:", dni);
    const pacienteExistente = await pool.query(
      "SELECT id_paciente, nombre, dni, celular FROM pacientes WHERE dni = $1",
      [dni]
    );

    let paciente;

    if (pacienteExistente.rows.length > 0) {
      paciente = pacienteExistente.rows[0];
      console.log("✅ Paciente ya existe en BD:", paciente);

      if (
        paciente.celular !== telefonoStr &&
        paciente.celular !== String(telefono)
      ) {
        console.log("📱 Actualizando teléfono del paciente...");
        await pool.query(
          "UPDATE pacientes SET celular = $1 WHERE id_paciente = $2",
          [telefonoStr, paciente.id_paciente]
        );
        console.log("✅ Teléfono actualizado");
      }
    } else {
      console.log("💾 Creando nuevo paciente en BD...");
      const nuevoResult = await pool.query(
        "INSERT INTO pacientes (nombre, dni, celular) VALUES ($1, $2, $3) RETURNING *",
        [nombreCompleto, dni, telefonoStr]
      );

      paciente = nuevoResult.rows[0];
      console.log("✅ Nuevo paciente creado:", paciente);
    }

    const response = {
      mensaje: `✅ DNI validado con éxito\n\n${nombreCompleto}`,
    };

    console.log("📤 Enviando respuesta:");
    console.log(JSON.stringify(response, null, 2));
    console.log("====== FIN PETICIÓN EXITOSA ======\n");

    res.json(response);
  } catch (error) {
    console.error("Tipo de error:", error.name);
    console.error("Mensaje:", error.message);
    console.error("Stack:", error.stack);

    res.status(500).json({
      mensaje:
        "❌ Ocurrió un error al verificar tu DNI. Por favor, intenta nuevamente.",
    });
  }
});

app.listen(port, () => {
  console.log(`\n🚀 Servidor corriendo en http://localhost:${port}`);
  console.log(`📡 Endpoints disponibles:`);
  console.log(`   - http://localhost:${port}/medicos`);
  console.log(`   - http://localhost:${port}/citas\n`);
});
