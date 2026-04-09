# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportarCSVWizard(models.TransientModel):
    _name = 'importar.csv.wizard'
    _description = 'Importar CSV de Asistencias'

    archivo_csv = fields.Binary(
        string='Archivo CSV',
        required=True,
        attachment=False,
    )
    nombre_archivo = fields.Char(string='Nombre del archivo')
    resultado = fields.Text(string='Resultado', readonly=True)

    def action_importar(self):
        """
        Lee el CSV exportado por el biométrico.
        Columnas esperadas: User, WorkId, CardNo, Date, Time, IN/OUT, EventCode
        Solo importa filas donde IN/OUT == 'IN'.
        Busca el nombre del contacto en res.partner por campo VAT (cédula).
        """
        if not self.archivo_csv:
            raise UserError(_('Por favor selecciona un archivo CSV.'))

        # Decodificar el archivo
        try:
            contenido = base64.b64decode(self.archivo_csv).decode('utf-8', errors='replace')
        except Exception:
            raise UserError(_('No se pudo leer el archivo. Asegúrate de que sea un CSV válido.'))

        # Detectar el dialecto (coma o punto y coma)
        try:
            dialecto = csv.Sniffer().sniff(contenido[:2048], delimiters=',;\t')
        except csv.Error:
            dialecto = csv.excel  # Por defecto, coma

        lector = csv.DictReader(io.StringIO(contenido), dialect=dialecto)

        # Normalizar los nombres de columnas (quitar espacios y comillas)
        def limpiar(valor):
            if valor is None:
                return ''
            return str(valor).strip().strip("'\"")

        AsistenciaEntrada = self.env['asistencia.entrada']
        Employee = self.env['hr.employee']

        importados = 0
        omitidos = 0
        sin_empleado = 0
        errores = []

        for num_fila, fila in enumerate(lector, start=2):
            # Normalizar claves del CSV
            fila_limpia = {k.strip().strip("'\""): limpiar(v) for k, v in fila.items() if k}

            # Obtener tipo de registro (IN/OUT)
            tipo = fila_limpia.get('IN/OUT', '').upper()
            if tipo != 'IN':
                omitidos += 1
                continue

            # Obtener cédula desde CardNo
            cedula = fila_limpia.get('CardNo', '').strip()
            if not cedula or cedula.upper() == 'NULL':
                # Intentar con WorkId si CardNo es nulo
                cedula = fila_limpia.get('WorkId', '').strip()
            if not cedula or cedula.upper() == 'NULL':
                omitidos += 1
                continue

            # Obtener fecha y hora
            fecha_str = fila_limpia.get('Date', '')
            hora_str = fila_limpia.get('Time', '')

            if not fecha_str:
                errores.append(f'Fila {num_fila}: fecha vacía, se omite.')
                omitidos += 1
                continue

            # Parsear fecha (formato esperado: YYYY-MM-DD)
            try:
                from datetime import datetime
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                except ValueError:
                    errores.append(f'Fila {num_fila}: formato de fecha no reconocido ({fecha_str}).')
                    omitidos += 1
                    continue

            # (Eliminada validación de fecha de hoy para permitir subir el histórico completo)

            # Limpiar la cédula del CSV para dejar solo números (por si viene con ceros, a la izquierda)
            cedula_limpia = ''.join(filter(str.isdigit, cedula))
            
            # Buscar empleado por el campo Número de Identificación (identification_id)
            employee = False
            if cedula_limpia:
                # 1. Búsqueda en Identificación exacta
                employee = Employee.search([('identification_id', '=', cedula_limpia)], limit=1)
                
                # 2. Búsqueda ilike por si lo guardaron con V-, E-, puntos, etc.
                if not employee:
                    employee = Employee.search([('identification_id', 'ilike', '%' + cedula_limpia + '%')], limit=1)
                    
                # 3. Búsqueda alternativa usando el nombre (si el WorkId era el nombre)
                if not employee and not cedula_limpia.isdigit():
                    employee = Employee.search([('name', 'ilike', cedula)], limit=1)

            # Validar e informar si no se encontró
            employee_id = employee.id if employee else False
            nombre_empleado = employee.name if employee else f'🔴 NO ENCONTRADO ({cedula})'
            if not employee:
                sin_empleado += 1
                errores.append(f'Fila {num_fila}: La persona con cédula {cedula} no existe en empleados.')

            # Verificar si ya existe este registro para evitar duplicados
            existe = AsistenciaEntrada.search([
                ('cedula', '=', cedula),
                ('fecha', '=', fecha),
                ('hora', '=', hora_str),
            ], limit=1)

            if existe:
                omitidos += 1
                continue

            # Crear el registro
            AsistenciaEntrada.create({
                'cedula': cedula,
                'fecha': fecha,
                'hora': hora_str,
                'employee_id': employee_id,
                'nombre_empleado': nombre_empleado,
            })
            importados += 1

        # Construir mensaje de resultado
        resumen = (
            f'✅ Importados: {importados} registros de entrada.\n'
            f'⏭️ Omitidos (OUT, duplicados o sin cédula): {omitidos}\n'
            f'⚠️ Sin empleado en Odoo: {sin_empleado}\n'
        )
        if errores:
            resumen += '\nERRORES:\n' + '\n'.join(errores[:20])

        # Actualizar el resultado en el wizard para mostrarlo
        self.resultado = resumen

        # Retornar la vista recargada del wizard con el resultado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'importar.csv.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_ver_registros(self):
        """Cierra el wizard y abre la lista de asistencias."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asistencias de Entrada',
            'res_model': 'asistencia.entrada',
            'view_mode': 'list,form',
            'target': 'current',
        }
