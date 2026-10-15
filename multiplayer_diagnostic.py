"""Run the network regressions on the user's real Winsock without starting a run."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import io
import platform
import sys
import unittest
from pathlib import Path
from release_info import RELEASE_ID,audit

def run():
    output=io.StringIO();suite=unittest.TestSuite()
    from network_test import NetworkTests
    from coop_test import CoopTests
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NetworkTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(CoopTests))
    from expedition_test import LegendCoopTests
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(LegendCoopTests))
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    errors=audit();root=Path(__file__).resolve().parent
    text='\n'.join([f'SIGMA TRINITY {RELEASE_ID} / DIAGNÓSTICO MULTIPLAYER',
        f'Sistema: {platform.platform()}',f'Python: {sys.version}',f'Pasta: {root}',
        'Integridade: '+('OK' if not errors else '; '.join(errors)),
        'Teste local TCP: criação, entrada, quatro participantes, sincronização e desconexão.',
        'Este teste não valida a rede Radmin, o firewall ou a ligação entre dois PCs.',
        '',output.getvalue(),'Logs técnicos: logs/multiplayer.log'])
    path=root/'DIAGNOSTICO_MULTIPLAYER.txt'
    try:path.write_text(text,encoding='utf-8')
    except OSError:pass
    print(text);return 0 if result.wasSuccessful() and not errors else 1

if __name__=='__main__':raise SystemExit(run())
