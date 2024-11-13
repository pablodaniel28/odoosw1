# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class colegio(models.Model):
    _name = 'colegio.colegio'
    _description = 'colegio.colegio'

    name = fields.Char()