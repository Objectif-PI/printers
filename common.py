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

PRINTER_STATES = [
    ('3', 'Idle'),
    ('4', 'Printing'),
    ('5', 'Stopped'),
]

JOB_STATES = [
    ('3', 'Pending'),
    ('4', 'Pending Held'),
    ('5', 'Processing'),
    ('6', 'Processing Stopped'),
    ('7', 'Canceled'),
    ('8', 'Aborted'),
    ('9', 'Completed'),
]

JOB_STATE_REASONS = [
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
    ('job-incoming', 'Files are currently being received'),
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
]
