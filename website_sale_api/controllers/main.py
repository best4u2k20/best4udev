# -*- coding: utf-8 -*-
import hashlib

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.osv import expression


class WebsiteSaleAPI(WebsiteSale):

    @staticmethod
    def _get_api_search_domain(search, category, attrib_values, search_in_description=True):
        domains = [[("sale_ok", "=", True)]]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)

    @staticmethod
    def image_url(record, field, size=None):
        sudo_record = record.sudo()

        if not sudo_record[field]:
            return False
        
        sha = hashlib.sha1(str(getattr(sudo_record, '__last_update')).encode('utf-8')).hexdigest()[0:7]
        size = '' if size is None else '/%s' % size
        return '/web/image/%s/%s/%s%s?unique=%s' % (record._name, record.id, field, size, sha)

    def _products_to_json(self, products, max_depth=1, fields=None):
        if fields is None:
            fields = [
                'id',
                'name',
                'display_name',
                'description',
                'description_purchase',
                'description_sale',
                'price',
                'list_price',
                'volume',
                'volume_uom_name',
                'weight',
                'weight_uom_name',
                'sale_ok',
                'purchase_ok',
                'is_product_variant',
                'product_variant_count',
                'qty_available',
                'virtual_available',
                'incoming_qty',
                'outgoing_qty',
                'website_url'
            ]

        result = []

        for product in products:
            product_json = {
                'image_128': self.image_url(product, 'image_128'),
                'image_256': self.image_url(product, 'image_256'),
                'image_512': self.image_url(product, 'image_512'),
                'image_1024': self.image_url(product, 'image_1024')
            }

            for field in fields:
                if field.endswith('_id') or field.endswith('_ids'):
                    product_json[field] = product[field].read()
                else:
                    product_json[field] = product[field]

            if max_depth > 0:
                product_json['currency_id'] = product['currency_id'].read(
                    fields=[
                        'id', 'display_name', 'symbol', 'decimal_places', 'currency_unit_label',
                        'currency_subunit_label'
                    ]
                )
                product_json['product_variant_ids'] = self._products_to_json(product['product_variant_ids'],
                                                                             max_depth=max_depth - 1)

            result.append(product_json)

        return result

    def _categories_to_json(self, categories):
        result = []

        for categ in categories:
            categ_json = {
                'id': categ['id'],
                'name': categ['name'],
                'display_name': categ['display_name'],
                'image_128': self.image_url(categ, 'image_128'),
                'image_256': self.image_url(categ, 'image_256'),
                'image_512': self.image_url(categ, 'image_512'),
                'image_1024': self.image_url(categ, 'image_1024'),
                'child_id': self._categories_to_json(categ['child_id'])
            }

            result.append(categ_json)

        return result


    @http.route('/shop/api/products', type='json', auth='public', website=True)
    def products(self, page=0, category=None, search='', ppg=20, **post):
        Category = request.env['product.public.category'].sudo()
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
        else:
            category = Category

        domain = self._get_api_search_domain(search, category, [])
        print(domain)
        # pricelist_context, pricelist = self._get_pricelist_context()
        # request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        if search:
            post["search"] = search

        Product = request.env['product.template'].with_context(bin_size=True).sudo()

        search_product = Product.search(domain)

        product_count = len(search_product)
        # pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=ppg * page, order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])

        # layout_mode = request.session.get('website_sale_shop_layout_mode')
        # if not layout_mode:
        #     if request.website.viewref('website_sale.products_list_view').active:
        #         layout_mode = 'list'
        #     else:
        #         layout_mode = 'grid'

        values = {
            'search': search,
            # 'category': category.read(),
            # 'pricelist': pricelist.read(),
            'products': self._products_to_json(products, max_depth=1),
            'search_count': product_count,  # common for all searchbox
            'ppg': ppg,
            # 'categories': categs.read(),
            'attributes': attributes.read(),

        }

        return values

    @http.route('/shop/api/categories', type='json', auth='public', website=True)
    def categories(self, categ_ids=None, **post):
        if categ_ids is None:
            categ_ids = []

        Category = request.env['product.public.category'].sudo()
        categs_domain = [('parent_id', '=', False)]

        if categ_ids:
            categs_domain.append(('id', 'in', categ_ids))

        categs = Category.search(categs_domain)

        values = {
            'categories': self._categories_to_json(categs)
        }

        return values