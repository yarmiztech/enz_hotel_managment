from odoo import fields,models,api


class RoomTypes(models.Model):
    _name = 'room.types'

    name = fields.Char()
    description = fields.Text()
    rent = fields.Float()

class HotelConfiguration(models.Model):
    _name = 'hotel.configuration'

    name = fields.Char()
    no_of_rooms = fields.Integer()
    no_of_floors = fields.Integer()
    room_lines = fields.One2many('room.configuration','hotel_id')

class RoomConfiguration(models.Model):
    _name = 'room.configuration'
    _rec_name = 'room_no'

    hotel_id = fields.Many2one('hotel.configuration')
    room_no = fields.Char()
    floor_no = fields.Char()
    room_type_id = fields.Many2one('room.types')
    no_of_adults = fields.Float()
    no_of_childrens = fields.Float()
    rent = fields.Float()

    @api.onchange('room_type_id')
    def compute_room_rent(self):
        self.rent = self.room_type_id.rent