# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers import main
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL, table_compute

main.PPR = 3
main.PPG = 16

class MedicalShop(website_sale):
    # @http.route([
    #     '/shop',
    #     '/shop/page/<int:page>',
    #     '/shop/category/<model("product.public.category"):category>',
    #     '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    # ], type='http', auth="public", website=True)
    # def shop(self, page=0, category=None, search='', **post):
    #     res = super(MedicalShop, self).shop(page, category, search, **post)

    #     BodyParts = request.env['product.public.body.part'].search([])
    #     res.qcontext['bodyparts'] = BodyParts

    #     res.qcontext['shop_home_page'] = False if category or search else True
    #     return res

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/bodypart/<int:bodypart>',
        '/shop/bodypart/<int:bodypart>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, bodypart=None, search='', view='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        shop_home_page = False if category or search or bodypart or view else True

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        domain = self._get_search_domain(search, category, attrib_values)
        if bodypart:
            bpart = request.env['product.public.body.part'].sudo().search(
                [('sequence', '=', bodypart)])
            domain += [('public_body_parts_ids', '=', bpart.id)]
            url = "/shop/bodypart/%s" % slug(bpart)
        if shop_home_page:
            domain += [('id', '=', 11500)]

        keep = QueryURL('/shop', category=category and int(category),
                        #bodypart=bodypart and int(bodypart),
                        search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"
        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list
        pager = request.website.pager(url=url, total=product_count, page=page, step=main.PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=main.PPG, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products),
            'rows': main.PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
            'shop_home_page': shop_home_page,
            'bodypart': bodypart,
            'view': view,
        }
        return request.website.render("website_sale.products", values)
