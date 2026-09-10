from odoo import models , api ,fields,_
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    def action_create_portal_user(self):
        self.ensure_one()

        if self.user_ids:
            raise ValidationError(_("Portal user already exists."))

        portal_group = self.env.ref("base.group_portal")

        self.env["res.users"].create({
            "name": self.name,
            "login": self.email,
            "email": self.email,
            "partner_id": self.id,  # Existing partner use hoga
            "group_ids": [(6, 0, [portal_group.id])],
        })