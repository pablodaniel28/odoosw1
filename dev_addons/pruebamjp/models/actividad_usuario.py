from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ActividadUsuario(models.Model):
    _name = 'pruebamjp.actividad_usuario'
    _description = 'Modelo o tabla actividad_usuario'

    visto = fields.Boolean(string='Visto', default=False, required=True)
    actividad_id = fields.Many2one('pruebamjp.actividad', string="Actividad", ondelete='cascade', required=True)
    usuario_recibe_id = fields.Many2one(
        'res.users', 
        string='Usuarios', 
        domain=lambda self: self._get_domain_usuarios(),
        required=True
    )
    tutor_usuario_info = fields.Char(
        string='Información del Tutor y Usuario', 
        compute='_compute_tutor_usuario_info'
    )
    
    # Campos relacionados para las fechas de la actividad
    fecha_inicio = fields.Datetime(string="Fecha Inicio", related="actividad_id.fecha_inicio", store=True)
    fecha_fin = fields.Datetime(string="Fecha Fin", related="actividad_id.fecha_fin", store=True)

    _sql_constraints = [
        ('unique_actividad_usuario', 'unique(actividad_id, usuario_recibe_id)', 'El usuario ya ha recibido esta actividad.')
    ]

    @api.model
    def _get_domain_usuarios(self):
        tutores = self.env['pruebamjp.tutor'].search([])
        usuario_ids = tutores.mapped('usuario_id.id')
        return [('id', 'in', usuario_ids)]

    @api.depends('usuario_recibe_id')
    def _compute_tutor_usuario_info(self):
        for record in self:
            if record.usuario_recibe_id:
                tutor = self.env['pruebamjp.tutor'].search([('usuario_id', '=', record.usuario_recibe_id.id)], limit=1)
                if tutor:
                    curso = tutor.estudiante_tutor.estudiante.inscripcion_ids.curso
                    record.tutor_usuario_info = f"Tutor: {tutor.nombre} {tutor.apellido}, Curso: {curso.nombre} {curso.paralelo} - {curso.ciclo_id.nombre}"
                else:
                    record.tutor_usuario_info = f"Usuario: {record.usuario_recibe_id.name}"
            else:
                record.tutor_usuario_info = "No asignado"

    @api.model
    def default_get(self, fields_list):
        res = super(ActividadUsuario, self).default_get(fields_list)
        user = self.env.user
        if 'usuario_envia_id' in fields_list:
            res['usuario_envia_id'] = user.id
        return res

    def _create_actividad_usuarios(self, users):
        actividad_usuario_model = self.env['pruebamjp.actividad_usuario']
        for user in users:
            actividad_usuario_model.create({
                'visto': False,
                'actividad_id': self.id,
                'usuario_recibe_id': user.id,
            })
