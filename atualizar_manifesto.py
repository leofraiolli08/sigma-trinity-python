"""Regenerate the installation manifest after intentional development changes."""
import hashlib
import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    files = {}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(x.startswith('.') for x in p.relative_to(root).parts) or '__pycache__' in p.parts:
            continue
        include = p.suffix in ('.py', '.bat') or p.name == 'requirements.txt' or (p.is_relative_to(root / 'assets') and not p.is_relative_to(root / 'assets/music'))
        if include:
            files[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    (root / 'release_manifest.json').write_text(json.dumps({'release': 'V10', 'files': files}, indent=2), encoding='utf-8')
    print(f'Manifesto atualizado: {len(files)} arquivos.')

if __name__ == '__main__':
    main()
