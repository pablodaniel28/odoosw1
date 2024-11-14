from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Definición de la clase estudiante, que hereda de models.Model
class estudiante(models.Model):
    # Nombre técnico del modelo que se usará en la base de datos (prefijo 'pruebamjp' para evitar conflictos)
    _name = 'pruebamjp.estudiante'
    # Descripción del modelo, útil para documentar el propósito del modelo
    _description = 'Modelo o tabla estudiante'

    # Campos del modelo
    nombre = fields.Char(readonly=False, required=True)  # Campo de texto para el nombre, requerido
    apellido = fields.Char(required=True)                # Campo de texto para el apellido, requerido
    edad = fields.Char(required=True)                    # Campo de texto para la edad, requerido
    # Relación One2many con el modelo 'nota'
    nota_ids = fields.One2many('pruebamjp.nota', 'estudiante_id', string="Estudiantes_nota")
    # Relación One2many con el modelo 'subnota'
    subnota_ids = fields.One2many('pruebamjp.subnota', 'estudiante_id', string="Estudiantes_subnota")
    # Relación One2many con el modelo 'inscripcion'
    inscripcion_ids = fields.One2many('pruebamjp.inscripcion', 'estudiante', string="Estudiantes")
    # Relación One2many con el modelo 'estudiante_tutor' (asociando estudiantes con sus tutores)
    estudiante_tutor = fields.One2many(string="estudiante_tutor", comodel_name="pruebamjp.estudiante_tutor", inverse_name='estudiante')
    usuario_id = fields.Many2one('res.users', string='Usuario',required=True)

    # Sobrescribe el método create para convertir 'nombre' y 'apellido' en mayúsculas al crear el registro
    @api.model
    def create(self, vals):
        if 'nombre' in vals:
            vals['nombre'] = vals['nombre'].upper()
        if 'apellido' in vals:
            vals['apellido'] = vals['apellido'].upper()
        return super(estudiante, self).create(vals)

    # Restricción para asegurar que 'nombre' y 'apellido' estén en mayúsculas
    @api.constrains('nombre', 'apellido')
    def _check_mayusculas(self):
        for record in self:
            if record.nombre != record.nombre.upper() or record.apellido != record.apellido.upper():
                raise ValidationError('Los campos nombre y apellido deben estar en mayúsculas.')

    # Campo calculado para mostrar el nombre completo del estudiante
    @api.depends('nombre', 'apellido') 
    def _compute_display_name(self): 
        for rec in self: 
            rec.display_name = f"{rec.nombre} {rec.apellido}"

    # Restricción de unicidad en 'nombre' y 'apellido' para evitar duplicados
    @api.constrains('nombre', 'apellido')
    def _check_unique_estudiante(self):
        for rec in self:
            existing_records = self.search([
                ('nombre', '=', rec.nombre),
                ('apellido', '=', rec.apellido),
                ('id', '!=', rec.id)
            ])
            if existing_records:
                raise ValidationError('Ya existe el estudiante.')

    # Sobrescribe el método unlink (eliminar) para evitar eliminar estudiantes con inscripciones o tutores asociados
    def unlink(self):
        for estudiantes in self:
            if estudiantes.inscripcion_ids or estudiantes.estudiante_tutor:
                raise ValidationError("No se puede eliminar el estudiante porque tiene inscripciones o tutores relacionados.")
        return super(estudiante, self).unlink()
