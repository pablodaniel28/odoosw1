import logging
from odoo import http
from odoo.http import request
import json

_logger = logging.getLogger(__name__)

class ComunicadoController(http.Controller):

    @http.route('/api/comunicados/general', auth='public', type='http', methods=['GET'], csrf=False)
    def get_comunicados_general(self, **kwargs):
        _logger.info("Iniciando obtención de comunicados para el usuario.")
        
        # Verifica que la consulta se realiza correctamente
        comunicados = request.env['pruebamjp.comunicado_usuario'].sudo().search([])
        data = []  # Definimos la lista `data` aquí para evitar errores

        seen_ids = set()  # Usamos un conjunto para evitar duplicados

        for com in comunicados:
            # Evitar procesar comunicados duplicados
            if com.comunicado_id.id not in seen_ids:
                seen_ids.add(com.comunicado_id.id)  # Añadir el ID al conjunto

                comunicado = com.comunicado_id
                multimedia_data = []

                # Procesamos los enlaces multimedia
                if comunicado.audio_url:
                    multimedia_data.append({
                        'name': 'Audio',
                        'type': 'audio/mpeg',
                        'url': comunicado.audio_url
                    })
                if comunicado.video_url:
                    multimedia_data.append({
                        'name': 'Video',
                        'type': 'video/mp4',
                        'url': comunicado.video_url
                    })
                if comunicado.imagen_url:
                    multimedia_data.append({
                        'name': 'Imagen',
                        'type': 'image/png',
                        'url': comunicado.imagen_url
                    })

                # Agregamos los adjuntos de Odoo, si existen
                for attachment in comunicado.attachment_ids:
                    multimedia_data.append({
                        'name': attachment.name,
                        'type': attachment.mimetype,
                        'url': f"/web/content/{attachment.id}?download=true" if attachment.datas else None
                    })

                # Construir los datos del comunicado
                comunicado_data = {
                    'nombre': comunicado.nombre,
                    'descripcion': comunicado.description,
                    'fecha': comunicado.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                    'visto': com.visto,
                    'multimedia': multimedia_data
                }
                
                # Log de cada comunicado procesado
                _logger.info("Comunicado procesado: %s", json.dumps(comunicado_data, indent=2))
                data.append(comunicado_data)

        # Log de los datos finales que se enviarán
        _logger.info("Datos finales enviados en la respuesta: %s", json.dumps(data, indent=2))

        # Enviar la respuesta en formato JSON
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])
