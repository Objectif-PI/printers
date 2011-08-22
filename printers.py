# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2011 SYLEAM Info Services (http://www.syleam.fr)
#                         All rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields
from osv import osv


class printers_server(osv.osv):
    """
    Manage printing server
    """
    _name = 'printers.server'
    _description = 'List of printing server'

    _columns = {
        'server': fields.char('Server', size=64, required=True),
        'address': fields.char('Address', size=15, required=True),
        'port': fields.integer('Port'),
        'user': fields.char('User', size=32),
        'pass': fields.char('Password', size=32),
        'active': fields.boolean('Active'),
        'printer_ids': fields.one2many('printers.list', 'server_id', 'Printer list'),
    }

    _order = 'server'

    _rec_name = 'server'

printers_server()


class printers_manufacturer(osv.osv):
    """
    Manage printer per manufacturer
    """
    _name = "printers.manufacturer"
    _description = "Manufacturer"
    _order = 'name'
    _rec_name = 'name'

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'code': fields.char('Code', size=16),
        'website': fields.char('Website', size=128),
    }

printers_manufacturer()


class printers_type(osv.osv):
    """
    Printer per type
    """
    _name = 'printers.type'
    _description = 'List of printer type'
    _order = 'name'
    _rec_name = 'name'

    _columns = {
        'name': fields.char('Printer type', size=32, required=True, translate=True),
        'description': fields.char('Description', size=64, translate=True),
    }

printers_type()


class printers_list(osv.osv):
    """
    Manage printer
    """
    _name = 'printers.list'
    _description = 'List of printers per server'
    _order = 'name'

    _columns = {
        'name': fields.char('Printer name', size=64, required=True),
        'code': fields.char('Printer code', size=64, required=True),
        'server_id': fields.many2one('printers.server', 'Server', required=True),
        'type_id': fields.many2one('printers.type', 'Type', required=True),
        'active': fields.boolean('Active'),
        'manufac_id': fields.many2one('printers.manufacturer', 'Manufacturer', required=True),
    }

    _defaults = {
        'active': lambda *a: True,
    }

    def _command(self, cr, uid, printer_id, filename, context):
        printer = self.browse(cr, uid, printer_id)

        cmd = ['/usr/bin/lpr']
        if printer.server_id.address:
            if printer.server_id.port != 0:
                cmd.append('-H %s:%s' % (printer.server_id.address, str(printer.server_id.port)))
            else:
                cmd.append('-H %s' % (printer.server_id.address))

            if printer.server_id.user:
                cmd.append('-U %s' % printer.server_id.user)

        cmd.append('-P %s' % printer.code)
        cmd.append('%s' % filename)

        return ' '.join(cmd)

    def send_printer(self, cr, uid, printer_id, filename, context):
        return self._command(cr, uid, printer_id, filename, context)


printers_list()


class printers_label(osv.osv):
    """
    Label board
    """
    _name = 'printers.label'
    _description = 'Label board'

    _columns = {
        'type_id': fields.many2one('printers.type', 'Printer type', required=True),
        'name': fields.char('Name', size=64, required=True, ),
        'width': fields.integer('Width', help="Enter width in millimeter"),
        'height': fields.integer('Height', help="Enter height in millimeter"),
    }

printers_label()


class printers_language(osv.osv):
    """
    Language support per printer
    """
    _name = 'printers.language'
    _description = 'Printer language'

    _columns = {
        'name': fields.char('Name', size=32, required=True, translate=True),
        'code': fields.char('Code', size=16, required=True),
    }

printers_language()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
