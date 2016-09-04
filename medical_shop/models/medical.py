# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductPublicBodyPart(models.Model):
    _name = "product.public.body.part"
    _inherit = ["website.seo.metadata"]
    _description = "Public Body Part"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of body part.")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    public_body_parts_ids = fields.Many2many(
        'product.public.body.part',  string='Public Body Parts', help='Public Body Parts')
