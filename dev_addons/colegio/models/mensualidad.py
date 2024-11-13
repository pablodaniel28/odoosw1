from odoo import models, fields, api
from odoo.exceptions import ValidationError

class mensualidad(models.Model):
     _name = 'colegio.mensualidad'
     _description = 'Modelo o tabla mensualidad'

     monto = fields.Float(required=True)
     fecha = fields.Datetime(required=True)
     inscripcion_id = fields.Many2one('colegio.inscripcion', string="Inscripcion", ondelete='cascade', required=True)