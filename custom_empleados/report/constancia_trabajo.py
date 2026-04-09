# -*- coding: utf-8 -*-
from odoo import models, api
from datetime import date

def numero_a_letras(numero):
    indicador_negativo = ""
    if numero < 0:
        indicador_negativo = "MENOS "
        numero = abs(numero)

    entero = int(numero)
    decimal = int(round((numero - entero) * 100))

    def leer_decenas(numero):
        if numero < 10:
            return ["CERO", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"][numero]
        elif numero < 20:
            return ["DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"][numero - 10]
        elif numero < 30:
            if numero == 20:
                return "VEINTE"
            return "VEINTI" + leer_decenas(numero - 20)
        elif numero < 100:
            decenas = ["TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
            if numero % 10 == 0:
                return decenas[(numero // 10) - 3]
            else:
                return decenas[(numero // 10) - 3] + " Y " + leer_decenas(numero % 10)
        return ""

    def leer_centenas(numero):
        if numero < 100:
            return leer_decenas(numero)
        elif numero == 100:
            return "CIEN"
        elif numero < 1000:
            centenas = ["CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
            if numero % 100 == 0:
                return centenas[(numero // 100) - 1]
            return centenas[(numero // 100) - 1] + " " + leer_decenas(numero % 100)
        return ""

    def leer_miles(numero):
        if numero < 1000:
            return leer_centenas(numero)
        elif numero == 1000:
            return "MIL"
        elif numero < 2000:
            return "MIL " + leer_centenas(numero % 1000)
        elif numero < 1000000:
            if numero % 1000 == 0:
                return leer_centenas(numero // 1000) + " MIL"
            return leer_centenas(numero // 1000) + " MIL " + leer_centenas(numero % 1000)
        return ""

    def leer_millones(numero):
        if numero < 1000000:
            return leer_miles(numero)
        elif numero == 1000000:
            return "UN MILLÓN"
        elif numero < 2000000:
            return "UN MILLÓN " + leer_miles(numero % 1000000)
        elif numero < 1000000000000:
            if numero % 1000000 == 0:
                return leer_miles(numero // 1000000) + " MILLONES"
            return leer_miles(numero // 1000000) + " MILLONES " + leer_miles(numero % 1000000)
        return ""

    letras = leer_millones(entero)
    decimal_letras = leer_decenas(decimal) if decimal > 0 else "CERO"
    
    formatted_number = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{indicador_negativo}{letras} BOLÍVARES CON {decimal_letras} CÉNTIMOS {decimal:02d}/100 (Bs. {formatted_number})"

class ConstanciaTrabajoReport(models.AbstractModel):
    _name = 'report.custom_empleados.report_constancia_trabajo_template'
    _description = 'Constancia de Trabajo Report Engine'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.employee'].browse(docids)
        
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        hoy = date.today()
        fecha_expedicion = f"{hoy.day:02d} días del mes de {meses[hoy.month - 1]} del {hoy.year}"

        return {
            'docs': docs,
            'sueldo_a_letras': numero_a_letras,
            'fecha_expedicion': fecha_expedicion,
        }
