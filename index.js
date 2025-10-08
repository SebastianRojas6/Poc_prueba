import express from "express";
import pkg from "pg";
import dotenv from "dotenv";

dotenv.config();
const { Pool } = pkg;

const app = express();
app.use(express.json());
const port = process.env.PORT || 3000;

console.log("Iniciando servidor...");
console.log("DATABASE_URL configurado:", process.env.DATABASE_URL ? "✅ SÍ" : "❌ NO");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

pool.query("SELECT NOW()")
  .then(() => console.log("✅ Conexión a Supabase exitosa"))
  .catch(err => console.error("❌ Error conectando a Supabase:", err.message));

function formatMedicos(rows) {
  return rows.map((m, i) => `${i + 1}. ${m.nombre} (DNI: ${m.dni})`).join("\n");
}

function cleanString(str) {
  return str.replace(/[\u200B-\u200D\uFEFF]/g, "");
}

// Generar código de cita único
function generarCodigoCita() {
  const fecha = new Date();
  const dia = String(fecha.getDate()).padStart(2, '0');
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const anio = fecha.getFullYear();
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  return `C-${random}-${dia}${mes}${anio}`;
}

// Endpoint para listar médicos
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
      detail: error.message 
    });
  }
});

app.all("/citas", async (req, res) => {
  console.log("\n====== NUEVA PETICIÓN /citas ======");
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📥 Método:", req.method);
  console.log("📋 Body recibido:", JSON.stringify(req.body, null, 2));
  
  try {
    // Extraer teléfono del webhook de SendPulse
    const telefono = req.body?.[0]?.contact?.phone;
    console.log("📞 Teléfono extraído:", telefono);
    
    if (!telefono) {
      console.log("❌ No se encontró teléfono en la petición");
      return res.status(400).json({
        status: "error",
        mensaje: "No se pudo identificar tu número de teléfono"
      });
    }
    
    // Buscar paciente por teléfono
    console.log("🔍 Buscando paciente con teléfono:", telefono);
    const pacienteResult = await pool.query(
      "SELECT id_paciente, nombre, dni, celular FROM pacientes WHERE celular = $1",
      [telefono]
    );
    
    if (pacienteResult.rows.length === 0) {
      console.log("❌ Paciente no encontrado");
      return res.json({
        status: "error",
        mensaje: `No encontramos un paciente registrado con el número ${telefono}. Por favor contacta con la clínica para registrarte.`
      });
    }
    
    const paciente = pacienteResult.rows[0];
    console.log("✅ Paciente encontrado:", paciente);
    
    // Obtener un médico aleatorio
    console.log("🔍 Obteniendo médico aleatorio...");
    const medicoResult = await pool.query(
      "SELECT id_medico, nombre, dni FROM medicos ORDER BY RANDOM() LIMIT 1"
    );
    
    if (medicoResult.rows.length === 0) {
      console.log("❌ No hay médicos disponibles");
      return res.json({
        status: "error",
        mensaje: "No hay médicos disponibles en este momento"
      });
    }
    
    const medico = medicoResult.rows[0];
    console.log("✅ Médico asignado:", medico);
    
    // Obtener una consulta aleatoria
    console.log("🔍 Obteniendo tipo de consulta...");
    const consultaResult = await pool.query(
      "SELECT id_consulta, tipo, especialidad FROM consultas ORDER BY RANDOM() LIMIT 1"
    );
    
    if (consultaResult.rows.length === 0) {
      console.log("❌ No hay tipos de consulta disponibles");
      return res.json({
        status: "error",
        mensaje: "No hay tipos de consulta disponibles"
      });
    }
    
    const consulta = consultaResult.rows[0];
    console.log("✅ Consulta asignada:", consulta);
    
    const codigoCita = generarCodigoCita();
    console.log("🎫 Código de cita generado:", codigoCita);
    
    const fechaCita = new Date();
    fechaCita.setDate(fechaCita.getDate() + 1);
    const fechaFormateada = fechaCita.toISOString().split('T')[0]; // YYYY-MM-DD
    const hora = "10:00:00";
    
    console.log("📅 Fecha de cita:", fechaFormateada, hora);
    
    console.log("💾 Creando cita en la base de datos...");
    const insertResult = await pool.query(
      `INSERT INTO citas (codigo, id_paciente, id_medico, id_consulta, fecha, hora, estado)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [codigoCita, paciente.id_paciente, medico.id_medico, consulta.id_consulta, fechaFormateada, hora, 'Pendiente']
    );
    
    const citaCreada = insertResult.rows[0];
    console.log("✅ Cita creada exitosamente:", citaCreada);
    
    const fechaMostrar = new Date(fechaFormateada).toLocaleDateString('es-PE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    
    const mensaje = `✅ ¡Cita creada exitosamente!

📋 Código: ${codigoCita}
👤 Paciente: ${paciente.nombre}
🆔 DNI: ${paciente.dni}
👨‍⚕️ Médico: ${medico.nombre}
🏥 Especialidad: ${consulta.especialidad}
📅 Fecha: ${fechaMostrar}
🕐 Hora: ${hora.substring(0, 5)}
📌 Estado: Pendiente

Por favor, llega 10 minutos antes de tu cita.`;
    
    const response = {
      status: "ok",
      mensaje: mensaje,
      cita: {
        codigo: codigoCita,
        paciente: paciente.nombre,
        medico: medico.nombre,
        especialidad: consulta.especialidad,
        fecha: fechaFormateada,
        hora: hora,
        estado: 'Pendiente'
      }
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
      detail: error.message 
    });
  }
});

app.all("/verificar-dni", async (req, res) => {
  console.log("\n====== NUEVA PETICIÓN /verificar-dni ======");
  console.log("⏰ Hora:", new Date().toISOString());
  console.log("📥 Método:", req.method);
  console.log("📋 Body recibido:", JSON.stringify(req.body, null, 2));
  
  try {
    const body = req.body?.[0];
    const telefono = body?.contact?.phone;
    
    let dni = body?.info?.message?.channel_data?.message?.text?.body;
    
    if (!dni || dni.length < 8) {
      dni = body?.contact?.variables?.DNI_USUARIO;
    }
    
    console.log("📞 Teléfono extraído:", telefono);
    console.log("🆔 DNI extraído:", dni);
    
    if (!dni || dni.length < 8) {
      console.log("❌ DNI no válido o no encontrado");
      return res.json({
        status: "error",
        mensaje: "❌ Por favor, ingresa un DNI válido de 8 dígitos."
      });
    }
    
    if (!telefono) {
      console.log("❌ No se encontró teléfono en la petición");
      return res.json({
        status: "error",
        mensaje: "❌ No se pudo identificar tu número de teléfono."
      });
    }
    
    dni = dni.replace(/\D/g, '');
    
    if (dni.length !== 8) {
      console.log("❌ DNI no tiene 8 dígitos");
      return res.json({
        status: "error",
        mensaje: "❌ El DNI debe tener exactamente 8 dígitos."
      });
    }
    
    console.log("🔍 Consultando API de Quertium para DNI:", dni);
    
    const quertiumResponse = await fetch(`https://quertium.com/api/v1/reniec/dni/${dni}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${process.env.QUERTIUM_API_KEY}`
      }
    });
    
    if (!quertiumResponse.ok) {
      console.log("❌ Error en API de Quertium:", quertiumResponse.status);
      return res.json({
        status: "error",
        mensaje: "❌ No pudimos verificar tu DNI. Por favor, verifica que sea correcto."
      });
    }
    
    const quertiumData = await quertiumResponse.json();
    console.log("✅ Datos de Quertium:", quertiumData);
    
    const nombreCompleto = [
      quertiumData.primerNombre,
      quertiumData.segundoNombre,
      quertiumData.apellidoPaterno,
      quertiumData.apellidoMaterno
    ].filter(Boolean).join(' ');
    
    console.log("👤 Nombre completo:", nombreCompleto);
    
    console.log("🔍 Verificando si paciente existe en BD...");
    const pacienteExistente = await pool.query(
      "SELECT id_paciente, nombre, dni, celular FROM pacientes WHERE dni = $1",
      [dni]
    );
    
    let paciente;
    
    if (pacienteExistente.rows.length > 0) {
      // Paciente ya existe
      paciente = pacienteExistente.rows[0];
      console.log("✅ Paciente ya existe en BD:", paciente);
      
      // Actualizar teléfono si es diferente
      if (paciente.celular !== telefono) {
        console.log("📱 Actualizando teléfono del paciente...");
        await pool.query(
          "UPDATE pacientes SET celular = $1 WHERE id_paciente = $2",
          [telefono, paciente.id_paciente]
        );
        console.log("✅ Teléfono actualizado");
      }
      
    } else {
      // Crear nuevo paciente
      console.log("💾 Creando nuevo paciente en BD...");
      const nuevoResult = await pool.query(
        "INSERT INTO pacientes (nombre, dni, celular) VALUES ($1, $2, $3) RETURNING *",
        [nombreCompleto, dni, telefono]
      );
      
      paciente = nuevoResult.rows[0];
      console.log("✅ Nuevo paciente creado:", paciente);
    }
    
    const mensaje = `✅ ¡Hola ${nombreCompleto}!

Tu DNI ha sido verificado correctamente.
📱 Teléfono registrado: ${telefono}

Ahora puedes continuar con tu reserva de cita.`;
    
    const response = {
      status: "ok",
      mensaje: mensaje,
      paciente: {
        id: paciente.id_paciente,
        nombre: nombreCompleto,
        dni: dni,
        celular: telefono
      }
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
      mensaje: "❌ Ocurrió un error al verificar tu DNI. Por favor, intenta nuevamente.",
      detail: error.message 
    });
  }
});

app.listen(port, () => {
  console.log(`\n🚀 Servidor corriendo en http://localhost:${port}`);
  console.log(`📡 Endpoints disponibles:`);
  console.log(`   - http://localhost:${port}/medicos`);
  console.log(`   - http://localhost:${port}/citas\n`);
});