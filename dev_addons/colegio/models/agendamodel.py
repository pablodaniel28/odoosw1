from odoo import models, fields

class Agenda(models.Model):
    _name = 'colegio.agenda'
    _description = 'Agenda'

    # Agregamos el campo "nombre" como título para el evento en la agenda
    nombre = fields.Char(string="Nombre del Evento", required=True)
    description = fields.Text(string="Descripción")
    date_start = fields.Datetime(string="Fecha de Inicio", required=True)
    date_end = fields.Datetime(string="Fecha de Fin")
    event_type = fields.Selection([
        ('comunicado', 'Comunicado'),
        ('tarea', 'Tarea'),
        ('otro', 'Otro')
    ], string="Tipo de Evento")
    
    # Relación con actividades para asociarlas con la agenda
    actividad_ids = fields.One2many('colegio.actividad', 'agenda_id', string="Actividades Asociadas")
