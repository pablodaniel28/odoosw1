# -*- coding: utf-8 -*-
# from odoo import http


# class Ficct(http.Controller):
#     @http.route('/ficct/ficct', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ficct/ficct/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ficct.listing', {
#             'root': '/ficct/ficct',
#             'objects': http.request.env['ficct.ficct'].search([]),
#         })

#     @http.route('/ficct/ficct/objects/<model("ficct.ficct"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ficct.object', {
#             'object': obj
#         })

