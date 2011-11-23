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
from tools.translate import _
import subprocess
import os
import netsvc
import tempfile
import time

logger = netsvc.Logger()


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
        'fitplot': fields.boolean('Fitplot', help='If check, scales the print file to fit on the page'),
    }

    _defaults = {
        'active': lambda *a: True,
        'fitplot': lambda *a: False,
    }

    def _command(self, cr, uid, printer_id, filename, context=None):
        """
        Use stdin to send data to the printer with lp or lpr command
        """
        if context is None:
            context = {}

        if not os.path.exists(filename):
            raise osv.except_osv(_('Error'), _('File %s does not exists') % filename)

        printer = self.browse(cr, uid, printer_id, context=context)

        cmd = ['lp']
        if printer.server_id.address:
            if printer.server_id.port != 0:
                cmd.append('-h %s:%s' % (printer.server_id.address, str(printer.server_id.port)))
            else:
                cmd.append('-h %s' % (printer.server_id.address))

            if printer.server_id.user:
                cmd.append('-U %s' % printer.server_id.user)
        cmd.append('-d "%s"' % printer.code)

        if printer.fitplot:
            cmd.append('-o fitplot')

        logger.notifyChannel('printers', netsvc.LOG_INFO, 'File to print: %s' % filename)
        logger.notifyChannel('printers', netsvc.LOG_INFO, 'Commande to execute: %s' % ' '.join(cmd))

        fp = open(filename, 'r')
        commands = fp.read()
        fp.close()

        p = subprocess.Popen(' '.join(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (r_stdout, r_stderr) = p.communicate(commands)
        p.stdin.close()
        logger.notifyChannel('printers', netsvc.LOG_INFO, 'return: %s' % str(p.returncode))
        logger.notifyChannel('printers', netsvc.LOG_INFO, 'stdout: %s' % str(r_stdout))
        logger.notifyChannel('printers', netsvc.LOG_INFO, 'stderr: %s' % str(r_stderr))

        os.remove(filename)
        del p
        del fp
        del commands

        return True

    def send_printer(self, cr, uid, printer_id, filename, context=None):
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


class printer_jasper_conf(osv.osv):
    _name = 'printer.jasper.conf'
    _description = 'Configure the jasper to print with the printer'

    _columns = {
        'sequence': fields.integer('Sequence', required=True, help="Use to make a priority"),
        'active': fields.boolean('Active', help='if check, this object is always available'),
        'model_id': fields.many2one('ir.model', 'Model', required=True, help="Select the model where the configuration is linked"),
        'condition': fields.text('Condition', required=True, help="Add condition to validate the configuration to use, use:\n- c for context\n- o for object\n- time for date and hour\n- u for user\n eg: o.type == 'in'"),
        'printer_id': fields.many2one('printers.list', 'Printer', required=True, help="Printer use"),
        'jasper_document_id': fields.many2one('jasper.document', 'Document jasper', required=True, help="Document to print"),
        'default_user_printer': fields.boolean('Printer of the user', help="If check and if the users has got a default printer use it"),
    }

    _defaults = {
        'sequence': lambda *a: 100,
        'active': lambda *a: True,
        'condition': lambda *a: 'True',
        'default_user_printer': lambda *a: False,
    }

    def run(self, cr, uid, object_ids, model_id=None, expression_condition=None, context=None):
        """
        search the configuration to print and print it
        """
        jasper_document_obj = self.pool.get('jasper.document')

        if model_id:
            domain = [('model_id', '=', model_id)]
        else:
            domain = []

        ids = self.search(cr, uid, domain, context=context)

        if not expression_condition:
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            expression_condition = {
                'c': context,
                'time': time,
                'u': user,
            }

        for this in self.browse(cr, uid, ids, context=context):
            expr = eval(str(this.condition), expression_condition)
            if not expr:
                logger.notifyChannel('printer.jasper.conf', netsvc.LOG_DEBUG, 'This printer doesn t match with this object %s' % this.condition)
                continue

            document = jasper_document_obj.browse(cr, uid, this.jasper_document_id.id, context=context)
            option = {
                'id': document.id,
                'attachment': document.attachment,
                'attachment_use': document.attachment_use,
            }
            uri = '/openerp/bases/%s/%s' % (cr.dbname, document.report_unit)
            data = {}
            data['form'] = {}
            data['form']['params'] = (document.format, uri, document.mode, document.depth, option)
            data['form']['ids'] = object_ids
            data['model'] = this.model_id.model

            jasper = netsvc.LocalService('report.jasper.' + document.service)
            (res, format) = jasper.create(cr, uid, object_ids, data, context=context)

            filename = tempfile.mkstemp(prefix='openerp_printer-', suffix='-report.%s' % format)
            file_pdf = open(filename[1], 'w')
            file_pdf.write(res)
            file_pdf.close()
            printer_id = context.get('printer_id', this.printer_id.id)
            self.pool.get('printers.list').send_printer(cr, uid, printer_id, filename[1], context=context)
            return True
        return False

printer_jasper_conf()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
