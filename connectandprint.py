# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import octoprint.plugin
import flask
import time
import subprocess


class ConnectAndPrintPlugin(octoprint.plugin.EventHandlerPlugin, 
                                octoprint.plugin.RestartNeedingPlugin):

    def on_event(self, event, payload):
        if event == octoprint.events.Events.UPLOAD:
            self._logger.info(
                "Uploaded file detected, connecting and printing...")
            self._connect_and_print(payload["path"])

    def _connect_and_print(self, file_path):
        printer = self._printer

        if not printer.is_operational():
            printer.connect()
            cmd_str = "/home/pi/poweron"
            subprocess.run(cmd_str, shell=True)

        self._logger.info("Waiting for printer to connect...")
        timeout = 120  # 2 minutes in seconds
        start_time = time.time()

        while not printer.is_operational() and time.time() - start_time < timeout:
            if ((time.time() - start_time) % 10) == 0:
                cmd_str = "/home/pi/poweron"
                subprocess.run(cmd_str, shell=True)
                printer.connect()

            time.sleep(2)

        if printer.is_operational():
            printer.select_file(file_path, False)
            printer.start_print()
        else:
            self._logger.error("Printer connection timed out after 2 minutes.")

    def get_update_information(self):
        return dict(
            connectandprint=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                # Version check: github repository
                type="github_release",
                user="zebreus",
                repo="connectandprint",
                current=self._plugin_version,

                # Update method: pip
                pip="https://raw.githubusercontent.com/zebreus/connectandprint/{target_version}/connectandprint.py"
            )
        )

__plugin_name__ = "Connect And Print"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_version__ = "1.0.0"
__plugin_description__='Automatically connect to your printer on file upload and start printing'
__plugin_author__="Max Grallinger"
__plugin_url__="https://github.com/zebreus/connectandprint"
__plugin_license__="AGPLv3"
__plugin_implementation__ = ConnectAndPrintPlugin()
__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}