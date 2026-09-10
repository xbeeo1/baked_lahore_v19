import logging
from os import utime
from os.path import getmtime
from time import time

from odoo import models, fields, api, http, _
from odoo.http import SessionExpiredException

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"
    
    pos_hide_refund = fields.Boolean(
        string="Hide Refund Button",
        default=False,
        help="Hide Refund Button in POS"
    )
    # pos_hide_general_note = fields.Boolean(
    #     string="Hide General Note",
    #     default=False,
    #     help="Hide General Note in POS"
    # )
    pos_hide_customer_note = fields.Boolean(
        string="Hide Customer Note",
        default=False,
        help="Hide Custom Note in POS"
    )
    pos_hide_pricelist = fields.Boolean(
        string="Hide Pricelist Button",
        default=False,
        help="Hide Pricelist Button in POS"
    )
    pos_hide_cancel_order = fields.Boolean(
        string="Hide Cancel Order Button",
        default=False,
        help="Hide Cancel Order Button in POS"
    )
    # pos_hide_quotations_order = fields.Boolean(
    #     string="Hide Quotations Order Button",
    #     default=False,
    #     help="Hide Quotations Order Button in POS"
    # )
    pos_hide_actions = fields.Boolean(
        string="Hide Actions Button",
        default=False,
        help="Hide Actions Button in POS"
    )

    pos_hide_remove_button = fields.Boolean(
        string="Hide Remove Button",
        default=False,
        help="Hide Remove Button in POS"
    )

    pos_hide_price_Button = fields.Boolean(
        string="Hide Price Button",
        default=False,
        help="Hide Price Button in POS"
    )

    pos_hide_discount_Button = fields.Boolean(
        string="Hide Discount(%) Button",
        default=False,
        help="Hide Discount Button in POS"
    )
