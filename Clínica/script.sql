INSERT INTO pacientes (nombre, dni, celular) VALUES
('PILAR NOEMI CASTRO ARANDA', '20039752', '981223144'),
('CARLOS MENDOZA LOPEZ', '41234567', '987654321'),
('LUISA FERNANDEZ RAMIREZ', '42345678', '912345678'),
('JORGE SOTO PEREZ', '43456789', '922334455'),
('MARIA RIVERA GONZALES', '44567890', '933221100');

INSERT INTO medicos (nombre, dni) VALUES
('ANTHONY CASTILLO', '42523480'),
('CLAUDIO ARANDA', '44556677'),
('SOFIA MARTINEZ', '45612345'),
('ALEJANDRO LOPEZ', '46789012'),
('VERONICA DIAZ', '47890123');

-- Insertar consultas
INSERT INTO consultas (tipo, especialidad) VALUES
('Nueva Consulta', 'Ozonoterapia'),
('Control', 'Medicina General'),
('Emergencia', 'Traumatología'),
('Seguimiento', 'Cardiología'),
('Evaluación', 'Dermatología');

-- Insertar citas
INSERT INTO citas (codigo, id_paciente, id_medico, id_consulta, fecha, hora, estado) VALUES
('C-001-29092025', 1, 1, 1, '2025-09-29', '09:00:00', 'Pendiente'),
('C-002-30092025', 2, 2, 2, '2025-09-30', '10:15:00', 'Pendiente'),
('C-003-01102025', 3, 3, 3, '2025-10-01', '11:30:00', 'Atendido'),
('C-004-02102025', 4, 4, 4, '2025-10-02', '14:00:00', 'Pendiente'),
('C-005-03102025', 5, 5, 5, '2025-10-03', '15:45:00', 'Anulado');
