#
# details_tab.py
#
# Copyright (C) 2008 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#

import logging

import deluge.component as component
from deluge.common import fsize, is_url, fdate
from deluge.ui.gtkui.torrentdetails import Tab

log = logging.getLogger(__name__)


def fpeer_size_second(first, second):
    return "%s (%s)" % (first, fsize(second))


def fdate_blank(value):
    """Display value as date, eg 05/05/08 or blank"""
    if value > 0.0:
        return fdate(value)
    else:
        return ""


def str_yes_no(value):
    """Return Yes or No to bool value"""
    return _("Yes") if value else _("No")


class DetailsTab(Tab):
    def __init__(self):
        Tab.__init__(self)
        # Get the labels we need to update.
        # widget name, modifier function, status keys
        builder = component.get("MainWindow").get_builder()

        self._name = "Details"
        self._child_widget = builder.get_object("details_tab")
        self._tab_label = builder.get_object("details_tab_label")

        self.label_widgets = [
            (builder.get_object("summary_name"), None, ("name",)),
            (builder.get_object("summary_total_size"), fsize, ("total_size",)),
            (builder.get_object("summary_num_files"), str, ("num_files",)),
            (builder.get_object("summary_completed"), fdate_blank, ("completed_time",)),
            (builder.get_object("summary_date_added"), fdate, ("time_added",)),
            (builder.get_object("summary_private"), str_yes_no, ("private",)),
            (builder.get_object("summary_torrent_path"), None, ("save_path",)),
            (builder.get_object("summary_hash"), str, ("hash",)),
            (builder.get_object("summary_comments"), str, ("comment",)),
            (builder.get_object("summary_owner"), str, ("owner",)),
            (builder.get_object("summary_shared"), str_yes_no, ("shared",)),
            (builder.get_object("summary_pieces"), fpeer_size_second, ("num_pieces", "piece_length")),
        ]

    def update(self):
        # Get the first selected torrent
        selected = component.get("TorrentView").get_selected_torrents()

        # Only use the first torrent in the list or return if None selected
        if len(selected) != 0:
            selected = selected[0]
        else:
            # No torrent is selected in the torrentview
            self.clear()
            return

        # Get the torrent status
        status_keys = ["name", "total_size", "num_files", "time_added", "completed_time",
                       "save_path", "hash", "comment", "owner", "num_pieces", "piece_length",
                       "shared", "private"]

        session = component.get("SessionProxy")
        session.get_torrent_status(selected, status_keys).addCallback(self._on_get_torrent_status)

    def _on_get_torrent_status(self, status):
        # Check to see if we got valid data from the core
        if status is None:
            return

        # Update all the label widgets
        for widget in self.label_widgets:
            if widget[1] is not None:
                args = []
                try:
                    for key in widget[2]:
                        args.append(status[key])
                except Exception, e:
                    log.debug("Unable to get status value: %s", e)
                    continue

                txt = widget[1](*args)
            else:
                txt = status[widget[2][0]]

            if widget[0].get_text() != txt:
                if widget[2][0] == 'comment' and is_url(txt):
                    widget[0].set_markup('<a href="%s">%s</a>' % (txt, txt.replace('&', '&amp;')))
                else:
                    widget[0].set_markup(txt.replace('&', '&amp;'))

    def clear(self):
        for widget in self.label_widgets:
            widget[0].set_text("")
