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


{
    'name': 'Printers',
    'version': '1.1',
    'category': 'Tools',
    'description': """Allow to manage printers in OpenERP""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
    ],
    'images': [],
    'data': [
        'security/ir.model.access.csv',
        'menu_view.xml',
        'base_view.xml',
        'server_action_view.xml',
        'printers_view.xml',
        'printers_data.xml',
        'ir_cron_data.xml',
    ],

    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
