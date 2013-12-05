# -*- coding: utf-8 -*-
##############################################################################
#
#    printers module for OpenERP, Allow to manage printers un OpenERP
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
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

from openerp.osv import osv
from openerp.osv import fields
from tools.translate import _
from openerp.modules import get_module_path
from datetime import datetime
import unicodedata
import subprocess
import logging
import netsvc
import os
import sys
import cups

from reportlab.pdfgen import canvas
import time

logger = logging.getLogger('printers')


def convert(name):
    """Convert data with no accent and upper mode"""
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').replace('&', '').replace('_', '')


class printers_server(osv.Model):
    """
    Manages printing servers
    """
    _name = 'printers.server'
    _description = 'List of printing servers'
    _order = 'server'
    _rec_name = 'server'

    _columns = {
        'server': fields.char('Server', size=64, required=True, help='Name of the server'),
        'address': fields.char('Address', size=15, required=True, help='IP address or hostname of the server'),
        'port': fields.integer('Port', help='Port of the server'),
        'user': fields.char('User', size=32, help='User to log in on the server'),
        'password': fields.char('Password', size=32, help='Password to log in on the server'),
        'active': fields.boolean('Active', help='If checked, this server is useable'),
        'printer_ids': fields.one2many('printers.list', 'server_id', 'Printers List', help='List of printers available on this server'),
        'custom_user': fields.boolean('Custom User', help='Check this, if you want to use OpenERP User Name, instead of a specific user'),
    }

    _defaults = {
        'address': '127.0.0.1',
        'active': True,
        'port': 0,
        'custom_user': False,
    }

    def update_printers(self, cr, uid, ids, context=None):
        for server in self.browse(cr, uid, ids, context=context):
            kwargs = {'host': server.address}
            if server.port:
                kwargs['port'] = int(server.port)
            try:
                connection = cups.Connection(**kwargs)
            except:
                logger.warning('Update cups printers : Failed to connect to cups server %s (%s:%s)' % (server.server, server.address, server.port))
                continue

            # Update Printers
            printers = connection.getPrinters()
            existing_printer = [printer.code for printer in server.printer_ids]
            for name, printer_info in printers.iteritems():
                if not name in existing_printer:
                    self.pool.get('printers.list').create(cr, uid, {
                        'name': printer_info['printer-info'],
                        'code': name,
                        'server_id': server.id,
                    })
        return True

    def update_jobs(self, cr, uid, ids=None, context=None, which='not-completed'):
        job_obj = self.pool.get('printers.job')
        printer_obj = self.pool.get('printers.list')

        if ids is None:
            ids = self.search(cr, uid, [], context=context)

        # Update printers list, in order to ensure that jobs printers will be in OpenERP
        self.update_printers(cr, uid, ids, context=context)

        for server in self.browse(cr, uid, ids, context=context):
            kwargs = {'host': server.address}
            if server.port:
                kwargs['port'] = int(server.port)
            try:
                connection = cups.Connection(**kwargs)
            except:
                logger.warning('Update cups jobs : Failed to connect to cups server %s (%s:%s)' % (server.server, server.address, server.port))
                continue

            # Retrieve asked job data
            jobs_data = connection.getJobs(which_jobs=which, requested_attributes=[
                'job-name',
                'job-id',
                'printer-uri',
                'job-media-progress',
                'time-at-creation',
                'job-state',
                'job-state-reasons',
                'time-at-processing',
                'time-at-completed',
            ])
            for cups_job_id, job_data in jobs_data.items():
                job_ids = job_obj.search(cr, uid, [('jobid', '=', cups_job_id), ('server_id', '=', server.id)], context=context)
                job_values = {
                    'name': job_data.get('job-name', ''),
                    'server_id': server.id,
                    'jobid': cups_job_id,
                    'job_media_progress': job_data.get('job-media-progress', 0),
                    'time_at_creation': job_data.get('time-at-creation', ''),
                    'job_state': str(job_data.get('job-state', '')),
                    'job_state_reason': job_data.get('job-state-reasons', ''),
                    'time_at_creation': datetime.fromtimestamp(job_data.get('time-at-creation', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'time_at_processing': job_data.get('time-at-processing', 0) and datetime.fromtimestamp(job_data.get('time-at-processing', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'time_at_completed': job_data.get('time-at-completed', 0) and datetime.fromtimestamp(job_data.get('time-at-completed', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                }

                # Search for the printer in OpenERP
                printer_uri = job_data['printer-uri']
                printer_code = printer_uri[printer_uri.rfind('/') + 1:]
                printer_id = printer_obj.search(cr, uid, [('server_id', '=', server.id), ('code', '=', printer_code)], context=context)
                job_values['printer_id'] = printer_id[0]

                if job_ids:
                    job_obj.write(cr, uid, job_ids, job_values, context=context)
                else:
                    job_obj.create(cr, uid, job_values, context=context)


class printers_manufacturer(osv.Model):
    """
    Manage printer per manufacturer
    """
    _name = 'printers.manufacturer'
    _description = 'Printer manufacturer'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', size=32, required=True, help='Name of this manufacturer'),
        'code': fields.char('Code', size=16, help='Code of this manufacturer'),
        'website': fields.char('Website', size=128, help='Website address of this manufacturer'),
    }


class printers_type(osv.Model):
    """
    Printer per type
    """
    _name = 'printers.type'
    _description = 'List of printers types'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', size=32, required=True, translate=True, help='Name of this type'),
        'description': fields.char('Description', size=64, help='Description for this type'),
        'printer_ids': fields.one2many('printers.list', 'type_id', 'Printers'),
    }


class printers_list(osv.Model):
    """
    Manage printers
    """
    _name = 'printers.list'
    _description = 'List of printers per server'
    _order = 'name'

    _columns = {
        'name': fields.char('Printer Name', size=64, required=True, help='Printer\'s name'),
        'code': fields.char('Printer Code', size=64, required=True, help='Printer\'s code'),
        'server_id': fields.many2one('printers.server', 'Server', required=True, help='Printer server'),
        'type_id': fields.many2one('printers.type', 'Type', help='Printer type'),
        'active': fields.boolean('Active', help='If checked, this link  printer/server is active'),
        'manufacturer_id': fields.many2one('printers.manufacturer', 'Manufacturer', help='Printer\'s manufacturer'),
        'fitplot': fields.boolean('Fitplot', help='If checked, scales the print file to fit on the page'),
    }

    _defaults = {
        'active': True,
        'fitplot': False,
    }

    def _command(self, cr, uid, printer_id, print_type, print_data, context=None):
        """
        Use stdin to send data to the printer with lp or lpr command
        """
        if context is None:
            context = {}

        # lp command is not implemented on Windows
        if sys.platform.startswith('win32'):
            raise osv.except_osv(_('Error'), _('The actual Server OS is a Windows platform. '
                                               'The printing lp command is not implemented. Unable to print !'))

        # Retrieve printer
        printer = self.browse(cr, uid, printer_id, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Generate the command line
        command = ['lp']
        if printer.server_id.address:
            # Add the server and port (if needed) in command line
            if printer.server_id.port != 0:
                command.append('-h %s:%s' % (printer.server_id.address, str(printer.server_id.port)))
            else:
                command.append('-h %s' % printer.server_id.address)

            # Add the user login in command line
            if printer.server_id.user and not printer.server_id.custom_user:
                command.append('-U %s' % printer.server_id.user)
            elif printer.server_id.custom_user:
                command.append('-U "%s"' % convert(user.name))

        # Add the printer code in command line
        command.append('-d "%s"' % printer.code)

        # Add Job name if define on the context
        if context.get('jobname', ''):
            command.append('-t "%s"' % context['jobname'])

        # Add the fitplot option in command line, if needed
        if printer.fitplot:
            command.append('-o fitplot')

        # Initialize printing data variable
        print_commands = None

        if print_type == 'report':
            # Retrieve data to generate the report
            report_data = self.pool.get('ir.actions.report.xml').read(cr, uid, print_data['report_id'], ['model', 'report_name'], context=context)
            report_service = netsvc.LocalService('report.' + report_data['report_name'])
            datas = {'ids': print_data['print_ids'], 'model': report_data['model']}

            # Log the command to send
            logger.info('Object to print : %s (%s)' % (datas['model'], repr(datas['ids'][0])))
            logger.info('Report to print : %s (%s)' % (report_data['report_name'], print_data['report_id']))

            # The commit is necessary for Jasper find the data in PostgreSQL
            cr.commit()
            # Generate the file to print
            (print_commands, format) = report_service.create(cr, uid, print_data['print_ids'], datas, context=context)
        elif print_type == 'file':
            # Check if the file exists
            if not os.path.exists(print_data['filename']):
                raise osv.except_osv(_('Error'), _('File %s does not exist !') % print_data['filename'])

            # Log the file name to print
            logger.info('File to print : %s' % print_data['filename'])

            # Retrieve contents of the file
            print_file = open(print_data['filename'], 'r')
            print_commands = print_file.read()
            print_file.close()
        elif print_type == 'raw':
            print_commands = print_data
            command.append('-o raw')
        else:
            raise osv.except_osv(_('Error'), _('Unknown command type, unable to print !'))

        # Create the command to send
        command = ' '.join(command)

        # Run the subprocess to send the commands to the server
        logger.info('Command to execute : %s' % command)
        sub_proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (result_stdout, result_stderr) = sub_proc.communicate(print_commands)
        sub_proc.stdin.close()

        # Log the return values
        logger.info('return : %s' % sub_proc.returncode)
        logger.info('stdout : %s' % result_stdout)
        logger.info('stderr : %s' % result_stderr)

        # Remove the file and free the memory
        del sub_proc
        del print_commands

        # Operation successful, return True
        return True

    def send_printer(self, cr, uid, printer_id, report_id, print_ids, context=None):
        """
        Sends a report to a printer
        """
        return self._command(cr, uid, printer_id, 'report', {'report_id': report_id, 'print_ids': print_ids}, context=context)

    def print_file(self, cr, uid, printer_id, filename, context=None):
        """
        Sends a file to a printer
        """
        if context is None:
            context = {}

        ctx = context.copy()
        if filename and not context.get('jobname'):
            ctx['jobname'] = filename.split('/')[-1]
        return self._command(cr, uid, printer_id, 'file', {'filename': filename}, context=ctx)

    def print_raw_data(self, cr, uid, printer_id, data, context=None):
        """
        Sends a file to a printer
        """
        return self._command(cr, uid, printer_id, 'raw', data, context=context)

    def print_test(self, cr, uid, ids, context=None):
        """
        Compose a PDF with printer information, and send it to the printer
        """
        if context is None:
            context = {}

        for printer in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            filename = "/tmp/test-printer-openerp-%d.pdf" % printer.id
            ctx['jobname'] = 'OpenERP Test Page (id: %d)' % printer.id

            c = canvas.Canvas(filename)
            c.drawString(100, 805, "Welcome to OpenERP printers module")
            c.drawString(100, 765, "Printer: %s" % printer.name)
            c.line(138, 760, 400, 760)
            c.drawString(100, 740, "Serveur: %s" % printer.server_id.server)
            c.line(145, 735, 400, 735)
            c.drawString(480, 805, time.strftime('%Y-%m-%d'))

            # Draw Rectangle
            c.line(20, 20, 570, 20)
            c.line(20, 820, 570, 820)
            c.line(20, 20, 20, 820)
            c.line(570, 820, 570, 20)

            # Titre en Haut
            c.line(20, 800, 570, 800)
            c.line(450, 800, 450, 820)

            # Add logo
            c.drawImage(os.path.join(get_module_path('printers'), 'static', 'src', 'img', 'logo.jpg'), 25, 730, 64, 64)
            c.save()

            # Send this file to the printer
            self.print_file(cr, uid, printer.id, filename, context=ctx)

        return True


class printers_label(osv.Model):
    """
    Label board
    """
    _name = 'printers.label'
    _description = 'Label board'

    _columns = {
        'type_id': fields.many2one('printers.type', 'Printer Type', required=True, help='Type of printer'),
        'name': fields.char('Name', size=64, required=True, help='Name of the label'),
        'width': fields.integer('Width', help='Width of the label, in millimeters'),
        'height': fields.integer('Height', help='Height of the label, in millimeters'),
    }


class printers_language(osv.Model):
    """
    Language support per printer
    """
    _name = 'printers.language'
    _description = 'Printer language'

    _columns = {
        'name': fields.char('Name', size=32, required=True, translate=True, help='Name of the language'),
        'code': fields.char('Code', size=16, required=True, help='Code of the language'),
    }


class printers_job(osv.Model):
    _name = 'printers.job'
    _description = 'Printing Job'
    _order = 'jobid'

    _columns = {
        'name': fields.char('Name', size=64, help='Job name'),
        'jobid': fields.integer('Job ID', required=True, help='CUPS id for this job'),
        'server_id': fields.many2one('printers.server', 'Server', required=True, help='Server which host this job'),
        'printer_id': fields.many2one('printers.list', 'Printer', required=True, help='Printer used for this job'),
        'job_media_progress': fields.integer('Media Progress', required=True, help='Percentage of progress for this job'),
        'time_at_creation': fields.datetime('Time At Creation', required=True, help='Date and time of creation for this job'),
        'time_at_processing': fields.datetime('Time At Processing', help='Date and time of process for this job'),
        'time_at_completed': fields.datetime('Time At Completed', help='Date and time of completion for this job'),
        'job_state': fields.selection([
            ('3', 'Pending'),
            ('4', 'Pending Held'),
            ('5', 'Processing'),
            ('6', 'Processing Stopped'),
            ('7', 'Canceled'),
            ('8', 'Aborted'),
            ('9', 'Completed'),
        ], 'State', help='Current state of the job'),
        'job_state_reason': fields.selection([
            ('none', 'No reason'),
            ('aborted-by-system', 'Aborted by the system'),
            ('compression-error', 'Error in the compressed data'),
            ('document-access-error', 'The URI cannot be accessed'),
            ('document-format-error', 'Error in the document'),
            ('job-canceled-at-device', 'Cancelled at the device'),
            ('job-canceled-by-operator', 'Cancelled by the printer operator'),
            ('job-canceled-by-user', 'Cancelled by the user'),
            ('job-completed-successfully', 'Completed successfully'),
            ('job-completed-with-errors', 'Completed with some errors'),
            ('job-completed(with-warnings', 'Completed with some warnings'),
            ('job-data-insufficient', 'No data has been received'),
            ('job-hold-until-specified', 'Currently held'),
            ('job-incomming', 'Files are currently being received'),
            ('job-interpreting', 'Currently being interpreted'),
            ('job-outgoing', 'Currently being sent to the printer'),
            ('job-printing', 'Currently printing'),
            ('job-queued', 'Queued for printing'),
            ('job-queued-for-marker', 'Printer needs ink/marker/toner'),
            ('job-restartable', 'Can be restarted'),
            ('job-transforming', 'Being transformed into a different format'),
            ('printer-stopped', 'Printer is stopped'),
            ('printer-stopped-partly', 'Printer state reason set to \'stopped-partly\''),
            ('processing-to-stop-point', 'Cancelled, but printing already processed pages'),
            ('queued-in-device', 'Queued at the output device'),
            ('resources-are-not-ready', 'Resources not available to print the job'),
            ('service-off-line', 'Held because the printer is offline'),
            ('submission-interrupted', 'Files were not received in full'),
            ('unsupported-compression', 'Compressed using an unknown algorithm'),
            ('unsupported-document-format', 'Unsupported format'),
        ], 'State Reason', help='Reason for the current job state'),
    }

    _sql_constraints = [
        ('jobid_unique', 'UNIQUE(jobid, server_id)', 'The jobid of the printers job must be unique per server !'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
