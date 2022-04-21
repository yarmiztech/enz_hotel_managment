from odoo import fields,models,api,_
from odoo.exceptions import UserError
from datetime import datetime,date

class SaleForm(models.Model):
    _name = 'sale.form'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.no') or '/'

        res = super(SaleForm, self).create(vals)
        return res

    name = fields.Char(string='Event No', required=True, index=True, copy=False, default='New', readonly=1)
    customer_id = fields.Many2one('res.partner')
    hotel_id = fields.Many2one('hotel.configuration')
    no_of_rooms = fields.Float()
    no_of_adults = fields.Float()
    no_of_childrens = fields.Float()
    order_lines = fields.One2many('sale.from.lines','sale_id')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done')],default='draft')
    adavance_lines = fields.One2many('account.payment','rent_id')
    salelines = fields.One2many('sale.order', 'rent_id')
    invoicelines = fields.One2many('account.move', 'rent_id')
    invoice_visibility = fields.Boolean()
    date = fields.Date(default=datetime.now().date())
    # advance_count = fields.Integer(compute='compute_advance_count')
    # sale_count = fields.Integer(compute='compute_sale_count')
    # invoice_count = fields.Integer(compute='compute_in')

    def create_invoice(self):
        self.invoice_visibility = True
        self.state = 'done'
        order_list = []
        product = self.env['product.template'].search([('name','=','Room Rent')])
        for line in self.order_lines:
            order_line = (0, 0, {
                'name': product.product_variant_id.name,
                'price_unit': line.rent,
                'product_id': product.product_variant_id.id,
                'product_uom_qty': line.no_of_rooms,
                'product_uom': product.uom_id.id,
                'tax_id': [(6, 0, line.tax_id.ids)]
            })
            order_list.append(order_line)
        if order_list:
            sale_id = self.env['sale.order'].create({
                'partner_id': self.customer_id.id,
                'rent_id': self.id,
                'rent_visibility': True,
                'order_line': order_list,
            })
            sale_id.action_confirm()
            invoices = sale_id._create_invoices()
            last_invoice = None
            for inv in invoices:
                inv.rent_id = self.id
                inv.rent_visibility = True
                inv.action_post()
                last_invoice = inv
            # if last_invoice:
            #     for advance in self.adavance_lines:
            #         last_invoice.js_assign_outstanding_line(advance.id)
            contract_obj = last_invoice
            contract_ids = []
            for each in contract_obj:
                contract_ids.append(each.id)
            view_id = self.env.ref('account.view_move_form').id
            if contract_ids:
                if len(contract_ids) <= 1:
                    value = {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Invoice'),
                        'res_id': contract_ids and contract_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', contract_ids)]),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'account.move',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Invoice'),
                        'res_id': contract_ids
                    }

                return value


        else:
            raise UserError('Noting To Invoice')

    def confirm(self):
        self.state = 'confirmed'

    def create_advance_payment(self):
        return {
            'name': 'Advance Payment',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_id': self.customer_id.id,
                'default_partner_type': 'customer',
                'search_default_inbound_filter': 1,
                'default_rent_id':self.id,
                'default_rent_visibility':True,
                'default_move_journal_types': ('bank', 'cash'),
            },

        }


class SaleFromLines(models.Model):
    _name = 'sale.from.lines'

    @api.model
    def default_tax_ids(self):
        vat_tax = self.env['account.tax'].search([('name', '=', 'Vat 15%'),('type_tax_use','=','sale')]).id
        tax_list = [(vat_tax)]
        return tax_list

    @api.onchange('room_type', 'hotel_id')
    def domain_sub_product(self):
        # Domian For Sub Product
        if self.room_type:
            if self.hotel_id.id:
                return {'domain': {
                    'room_ids': [('hotel_id', '=', self.hotel_id.id),
                                       ('room_type_id', '=', self.room_type.id)]}}
            # else:
            #     return {'domain': {'sub_product_id': [('parent_product_id', '=', self.product_id.id)]}}

    sale_id = fields.Many2one('sale.form')
    hotel_id = fields.Many2one('hotel.configuration')
    no_of_rooms = fields.Float()
    room_type = fields.Many2one('room.types')
    room_ids = fields.Many2many('room.configuration')
    tax_id = fields.Many2many('account.tax',default=default_tax_ids)
    rent = fields.Float()
    rent_subtotal = fields.Float()


    @api.onchange('no_of_rooms','rent')
    def compute_subtotal(self):
        self.rent_subtotal = self.no_of_rooms * self.rent

    @api.onchange('room_ids')
    def calaculte_length(self):
        self.no_of_rooms = len(self.room_ids)

    @api.onchange('room_type')
    def computr_price(self):
        self.rent = self.room_type.rent

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    rent_id = fields.Many2one('sale.form')
    rent_visibility = fields.Boolean()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rent_id = fields.Many2one('sale.form')
    rent_visibility = fields.Boolean()


class AccountMove(models.Model):
    _inherit = "account.move"

    rent_id = fields.Many2one('sale.form')
    rent_visibility = fields.Boolean()

