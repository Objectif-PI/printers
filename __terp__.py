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

{
    'name': 'Printers',
    'version': '1.0.1',
    'category': 'Tools',
    'description': """Manage printers in OpenERP""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'jasper_server',
    ],
    'init_xml': [],
    'update_xml': [
        #'security/groups.xml',
        'security/ir.model.access.csv',
        'view/menu.xml',
        'view/server_action.xml',
        'view/printers.xml',
        'view/users.xml',
        #'wizard/wizard.xml',
        #'report/report.xml',
        'data/printers.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'license': 'GPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
