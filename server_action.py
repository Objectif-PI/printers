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
import netsvc
import time

logger = netsvc.Logger()


class ir_actions_server(osv.osv):
    _inherit = 'ir.actions.server'

    def __init__(self, pool, cr):
        """
        Extend to add
        """
        super(ir_actions_server, self).__init__(pool, cr)
        logger.notifyChannel('init:module printers ', netsvc.LOG_INFO, 'Add printing as key')
        res = self._columns['state'].selection
        if 'printing' not in [k for k, v in res]:
            self._columns['state'].selection.append(('printing', 'Printing'))

    _columns = {
        'printing_configuration_type': fields.selection([('function', 'Use a function'), ('auto', 'Use configuration auto')], 'Type of configuration', help='You can selected your printer and jasper server by a python fonction\n or use the automatique configuration table'),
        'printing_source': fields.char('Source', size=256, help='Add condition to found the id of the printer, use:\n- c for context\n- o for object\n- time for date and hour\n- u for user\n eg: o.warehouse_id.printer_id.name'),
        'printing_function': fields.char('Function', size=64, help='name of the function to launch for printing'),
    }

    _defaults = {
        'printing_configuration_type': lambda *a: 'function',
        'printing_source': lambda *a: False,
        'printing_function': lambda *a: False,
    }

    def run(self, cr, uid, ids, context=None):
        """
        Execute by workflow
        """
        if context is None:
            context = {}
        printer_jasper_conf_obj = self.pool.get('printer.jasper.conf')

        result = False
        for action in self.browse(cr, uid, ids, context=context):
            logger.notifyChannel('printing.server.action', netsvc.LOG_DEBUG, 'Action: %s' % action.name)
            obj_pool = self.pool.get(action.model_id.model)
            obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
            ctx = {
                'context': context,
                'object': obj,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid
            }
            expr = eval(str(action.condition), ctx)
            if not expr:
                logger.notifyChannel('messaging.server.action', netsvc.LOG_DEBUG, 'This action doesn t match with this object %s' % action.condition)
                continue

            if action.state == 'printing':
                user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
                ctx = {
                    'c': context,
                    'o': obj,
                    'time': time,
                    'u': user,
                }
                if action.printing_configuration_type == 'function':
                    try:
                        printer_id = eval(str(action.printing_source), ctx)

                    except Exception, e:
                        print str(e)

                    logger.notifyChannel('server.action:printing', netsvc.LOG_DEBUG, 'Id of the printer: %s' % str(printer_id))

                    if action.printing_function:
                        getattr(obj, action.printing_function, None)(obj, printer_id, context)
                elif action.printing_configuration_type == 'auto':
                    printer_jasper_conf_obj.run(cr, uid, [context['active_id']], model_id=action.model_id.id, expression_condition=ctx, context=context)

            else:
                result = super(ir_actions_server, self).run(cr, uid, [action.id], context)

        return result

ir_actions_server()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
