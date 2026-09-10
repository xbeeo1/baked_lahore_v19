from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class VendorPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):

        partner = request.env.user.partner_id

        products = request.env['product.template'].sudo().search([
            ('vendor_id', '=', partner.id)
        ])

        return request.render(
            'cno_vendor_portal.portal_my_products',
            {
                'products': products,
                'page_name': 'products',
            }
        )

    # def _prepare_home_portal_values(self, counters):
    #
    #     values = super()._prepare_home_portal_values(counters)
    #
    #     if 'product_count' in counters:
    #         partner = request.env.user.partner_id
    #         values['product_count'] = request.env['product.template'].sudo().search_count([
    #             ('vendor_id', '=', partner.id)
    #         ])
    #
    #     return values