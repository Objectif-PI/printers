# -*- coding: utf-8 -*-
##############################################################################
#
#    printers module for OpenERP, Manage printers in OpenERP
#    Copyright (C) 2011 SYLEAM (<http://www.syleam.fr/>)
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#
#    This file is a part of printers
#
#    printers is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    printers is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields


class printers_user(osv.osv):
    """
    Gestion de l'imprimante de l'utilisateur
    """
    _inherit = 'res.users'

    _columns = {
        'context_printer_id': fields.many2one('printers.list', 'Printer by default'),
    }

printers_user()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
