#!/usr/bin/env python3
import deluge_exporter

import servicemanager
import win32event
import win32service
import win32serviceutil


class DelugeExporterWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "deluge_exporter"
    _svc_display_name_ = ""
    _svc_description_ = ""

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        deluge_exporter.start_exporter()

        while True:
            if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                break


if __name__ == "__main__":
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(DelugeExporterWindowsService)
    servicemanager.StartServiceCtrlDispatcher()
