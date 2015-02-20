# -*- coding: utf-8 -*-
##############################################################################
#
#    printers module for OpenERP, Allow to manage printers un OpenERP
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#    Copyright (C) 2015 Objectif-PI (<http://www.objectif-pi.com>).
#       Damien CRIER <damien.crier@objectif-pi.com>
#
#    This file is a part of printers
#
#    printers is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    printers is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models
from openerp import fields
from openerp import api
from openerp import _


class res_users(models.Model):

    """
    User\'s printer management
    """
    _inherit = 'res.users'

    context_printer_id = fields.Many2one('printers.list', string='Default printer', required=False, ondelete='restrict', help='Printer used by default for this user')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
