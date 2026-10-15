"""Identify this installation and verify packaged art/code before playing."""
from pathlib import Path
import hashlib
import json
import platform
import sys
from settings import BASE_DIR

RELEASE_ID='V10'
RELEASE_TITLE='PIXEL • EVOLUÇÕES E ASSINATURAS'

def audit(root=BASE_DIR):
    root=Path(root);errors=[]
    try:
        manifest=json.loads((root/'release_manifest.json').read_text(encoding='utf-8'))
        if not isinstance(manifest,dict) or manifest.get('release')!=RELEASE_ID or not isinstance(manifest.get('files'),dict) or not manifest['files']:
            return ['Manifesto de versão inválido ou pertencente a outro pacote.']
    except (OSError,ValueError):return ['release_manifest.json ausente ou inválido: extraia o pacote completo.']
    for relative,expected in manifest['files'].items():
        if not isinstance(relative,str) or not isinstance(expected,str) or len(expected)!=64:
            errors.append('Registro inválido no manifesto.');continue
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:
            errors.append('Caminho inválido no manifesto.');continue
        try:
            if hashlib.sha256((root/path).read_bytes()).hexdigest()!=expected:errors.append('Arquivo de outra versão ou alterado: '+relative)
        except OSError:errors.append('Arquivo ausente: '+relative)
    return errors

def report(errors=None,root=BASE_DIR):
    root=Path(root);errors=audit(root) if errors is None else errors
    lines=[f'SIGMA TRINITY {RELEASE_ID} — {RELEASE_TITLE}',f'Pasta executada: {root.resolve()}',
           f'Python: {sys.executable}',f'Sistema: {platform.system()} {platform.release()}',
           f'Integridade: {"OK — código e artes desta versão" if not errors else "INSTALAÇÃO INCOMPLETA OU MISTURADA"}',
           '']
    lines.extend(errors or ['Sete personagens em pixel art: 22 etapas com formas e ultimates próprias.',
                            'Interface pixelada e ícones de IA; chefe titã com folha independente.',
                            'Multiplayer: diagnóstico local em logs/multiplayer.log.',
                            'Seis mapas com monstros animados; especializações, objetivos e bestiário.',
                            'As folhas animadas substituem os monstros estáticos em todos os mapas.',
                            'Cutscenes de E/Q por estágio; protocolo cooperativo 7 nesta versão.'])
    lines.extend(['','Se estiver vendo o jogo antigo:',
                  '1. Feche todas as janelas do jogo e extraia o ZIP em uma pasta nova.',
                  f'2. Abra a pasta SIGMA_TRINITY_{RELEASE_ID} e execute JOGAR.bat dali.',
                  '3. Transfira somente save.json e os MP3; não copie código nem sprites antigos.'])
    return '\n'.join(lines)+'\n'

def write_diagnostic(errors=None,root=BASE_DIR):
    path=Path(root)/'DIAGNOSTICO.txt';content=report(errors,root)
    try:path.write_text(content,encoding='utf-8')
    except OSError:return content,None
    return content,path
