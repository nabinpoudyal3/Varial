import os
import subprocess
import time

import analysis
import diskio
import monitor
import settings
import toolinterface


class FwliteProxy(toolinterface.Tool):
    def __init__(self,
                 name=None,
                 py_exe=settings.fwlite_executable):
        super(FwliteProxy, self).__init__(name)
        self.py_exe = py_exe
        self._proxy = None

    def wanna_reuse(self, all_reused_before_me):

        if not os.path.exists(os.path.join(
                self.result_dir, 'fwlite_proxy.info')):
            return False
        proxy = diskio.read('fwlite_proxy')
        if not hasattr(proxy, 'results'):
            return False
        for name, smp in analysis.all_samples.iteritems():
            if not (
                name in proxy.samples
                and proxy.samples[name] == smp.input_files
            ):
                return False
        self._proxy = proxy
        return True

    def reuse(self):
        self._finalize()

    def run(self):
        self._proxy = analysis.fileservice('fwlite_proxy', False)
        self._proxy.event_files = dict(
            (s.name, s.input_files)
            for s in analysis.all_samples.itervalues()
        )
        diskio.write(self._proxy)
        proc = subprocess.Popen(
            ['python', self.py_exe],
            stdout=monitor._info.outstream,
            stderr=subprocess.STDOUT
        )
        while None == proc.returncode:
            time.sleep(0.2)
            proc.poll()
        self._finalize()

    def _finalize(self):
        for res in self._proxy.results:
            samplename = res.split('!')[0]
            analysis.fs_aliases += list(
                alias for alias in diskio.generate_fs_aliases(
                    os.path.join(self.result_dir, '%s.root' % res),
                    samplename
                )
            )