from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Actividad(models.Model):
    _name = 'pruebamjp.actividad'
    _description = 'Modelo o tabla de actividades'

    nombre = fields.Char(required=True)
    description = fields.Text(required=True)

    # Campos de fechas
    fecha_inicio = fields.Datetime(string="Fecha de Inicio", required=True)
    fecha_fin = fields.Datetime(string="Fecha Fin", required=True)

    # Campos multimedia
    video = fields.Binary(string="Video")
    imagen = fields.Binary(string="Imagen")
    audio = fields.Binary(string="Audio")

    # Relación con los usuarios que deben ver la actividad
    actividad_usuario_ids = fields.One2many('pruebamjp.actividad_usuario', 'actividad_id', string="Actividad")
    curso_id = fields.Many2one('pruebamjp.curso', string="Curso", required=True)
    agenda_id = fields.Many2one('pruebamjp.agenda', string="Agenda", ondelete='cascade')

    def create_actividad_for_course_users(self):
        if not self.curso_id:
            raise ValidationError("Por favor, seleccione un curso.")

        # Filtrar inscripciones del curso seleccionado
        max_year = self.env['pruebamjp.gestion'].search([], order='year desc', limit=1).year
        inscripciones = self.env['pruebamjp.inscripcion'].search([
            ('curso', '=', self.curso_id.id),
            ('gestion_id.year', '=', max_year)
        ])
        
        # Obtener los estudiantes inscritos en el curso
        estudiante_ids = inscripciones.mapped('estudiante.id')
        
        # Crear registros en actividad_usuario solo para los estudiantes del curso
        actividad_usuario_model = self.env['pruebamjp.actividad_usuario']
        for estudiante in estudiante_ids:
            usuario_id = self.env['pruebamjp.estudiante'].browse(estudiante).usuario_id.id
            actividad_usuario_model.create({
                'actividad_id': self.id,
                'usuario_recibe_id': usuario_id,
                'visto': False
            })

    @api.model
    def create(self, vals):
        record = super(Actividad, self).create(vals)
        record.create_actividad_for_course_users()
        return record

    @api.depends('nombre') 
    def _compute_display_name(self): 
        for rec in self: 
            rec.display_name = f"{rec.nombre}" 
