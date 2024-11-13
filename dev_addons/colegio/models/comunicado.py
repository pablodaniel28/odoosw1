from odoo import models, fields, api
from odoo.exceptions import ValidationError
import cloudinary
import cloudinary.uploader
import tempfile
import base64

# Configuración de Cloudinary
cloudinary.config(
    cloud_name="dl9isyqhf",
    api_key="591689814559583",
    api_secret="R2sOrAHU-OFSEnnIjpjZbvPnXBI"
)

class Comunicado(models.Model):
    _name = 'colegio.comunicado'
    _description = 'Modelo o tabla comunicado'

    nombre = fields.Char(required=True)
    description = fields.Text(required=True)
    fecha = fields.Datetime(required=True)

    # Campos multimedia (binarios)
    audio = fields.Binary(string="Audio")
    video = fields.Binary(string="Video")
    imagen = fields.Binary(string="Imagen")
    audio_url = fields.Char(string="Audio URL")
    video_url = fields.Char(string="Video URL")
    imagen_url = fields.Char(string="Imagen URL")

    # Campo para archivos adjuntos
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id', string="Archivos Adjuntos",
        domain=[('res_model', '=', 'colegio.comunicado')],
        help="Archivos adjuntos asociados con el comunicado."
    )

    comunicado_usuario_ids = fields.One2many('colegio.comunicado_usuario', 'comunicado_id', string="Comunicados")
    curso_id = fields.Many2one('colegio.curso', string="Curso")
    ciclo_id = fields.Many2one('colegio.ciclo', string="Ciclo")

    @api.model
    def create(self, vals):
        # Subir archivos multimedia a Cloudinary antes de crear el registro
        if 'audio' in vals and vals['audio']:
            with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
                temp_audio_file.write(base64.b64decode(vals['audio']))
                temp_audio_file.flush()
                audio_upload = cloudinary.uploader.upload(temp_audio_file.name, resource_type="video")
                vals['audio_url'] = audio_upload['url']
            vals.pop('audio', None)

        if 'video' in vals and vals['video']:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                temp_video_file.write(base64.b64decode(vals['video']))
                temp_video_file.flush()
                video_upload = cloudinary.uploader.upload(temp_video_file.name, resource_type="video")
                vals['video_url'] = video_upload['url']
            vals.pop('video', None)

        if 'imagen' in vals and vals['imagen']:
            with tempfile.NamedTemporaryFile(delete=False) as temp_image_file:
                temp_image_file.write(base64.b64decode(vals['imagen']))
                temp_image_file.flush()
                image_upload = cloudinary.uploader.upload(temp_image_file.name)
                vals['imagen_url'] = image_upload['url']
            vals.pop('imagen', None)

        # Crear el registro
        record = super(Comunicado, self).create(vals)
        return record

    def create_comunicado_for_all_users(self):
        users = self.env['res.users'].search([])
        self._create_comunicado_usuarios(users)

    def _create_comunicado_usuarios(self, users):
        comunicado_usuario_model = self.env['colegio.comunicado_usuario']
        for user in users:
            comunicado_usuario_model.create({
                'visto': 'no',
                'comunicado_id': self.id,
                'usuario_recibe_id': user.id,
            })

    def create_comunicado_for_tutors_of_course(self):
        if not self.curso_id:
            raise ValidationError("Por favor, seleccione un curso.")
        max_year = self.env['colegio.gestion'].search([], order='year desc', limit=1).year
        inscripciones = self.env['colegio.inscripcion'].search([
            ('curso', '=', self.curso_id.id),
            ('gestion_id.year', '=', max_year)
        ])
        estudiante_ids = inscripciones.mapped('estudiante.id')
        estudiante_tutores = self.env['colegio.estudiante_tutor'].search([('estudiante', 'in', estudiante_ids)])
        tutor_ids = estudiante_tutores.mapped('tutor.id')
        usuarios = self.env['res.users'].search([('id', 'in', self.env['colegio.tutor'].browse(tutor_ids).mapped('usuario_id.id'))])
        self._create_comunicado_usuarios(usuarios)

    def create_comunicado_for_ciclo(self):
        if not self.ciclo_id:
            raise ValidationError("Por favor, seleccione un ciclo (primaria o secundaria).")

        # Obtener el año más reciente de la gestión
        max_year = self.env['colegio.gestion'].search([], order='year desc', limit=1).year

        # Buscar inscripciones que coincidan con el ciclo y el año seleccionados
        inscripciones = self.env['colegio.inscripcion'].search([
            ('curso.ciclo_id', '=', self.ciclo_id.id),
            ('gestion_id.year', '=', max_year)
        ])

        # Obtener los IDs de los estudiantes en esas inscripciones
        estudiante_ids = inscripciones.mapped('estudiante.id')

        # Obtener los tutores de esos estudiantes
        estudiante_tutores = self.env['colegio.estudiante_tutor'].search([('estudiante', 'in', estudiante_ids)])
        tutor_ids = estudiante_tutores.mapped('tutor.id')

        # Obtener los usuarios asociados a esos tutores
        usuarios = self.env['res.users'].search([
            ('id', 'in', self.env['colegio.tutor'].browse(tutor_ids).mapped('usuario_id.id'))
        ])

        # Crear registros de comunicado para los usuarios filtrados
        self._create_comunicado_usuarios(usuarios)

    @api.depends('nombre')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.nombre}"

