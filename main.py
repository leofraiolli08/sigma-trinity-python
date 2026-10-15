"""Run from any working directory: python /path/to/sigma_trinity/main.py."""
import argparse
import os

def main():
    parser=argparse.ArgumentParser(description='SIGMA TRINITY: CHAOS ASCENSION')
    parser.add_argument('--debug',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--diagnose',action='store_true',help='Show version, executed folder and package integrity')
    parser.add_argument('--seed',type=int,default=1234)
    from settings import CHARACTERS
    parser.add_argument('--character',choices=list(CHARACTERS))
    parser.add_argument('--frames',type=int,help='Exit after N real loop frames (QA)')
    parser.add_argument('--headless',action='store_true',help='SDL dummy video/audio for automated QA')
    args=parser.parse_args()
    if args.headless or args.self_test:
        os.environ['SDL_VIDEODRIVER']='dummy'; os.environ['SDL_AUDIODRIVER']='dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
    if args.diagnose:
        from release_info import write_diagnostic,audit
        errors=audit();content,path=write_diagnostic(errors);print(content)
        if path:print('Relatório salvo em:',path)
        if errors:raise SystemExit(2)
    elif args.self_test:
        from self_test import run
        run()
    else:
        from release_info import audit,write_diagnostic
        errors=audit()
        if errors:
            content,path=write_diagnostic(errors);print(content)
            print('Não foi iniciado para evitar carregar sprites antigos. Extraia novamente o ZIP completo.')
            raise SystemExit(2)
        import pygame
        from game import Game
        try: Game(args.seed,args.debug,args.character).run(args.frames)
        finally: pygame.quit()

if __name__=='__main__': main()
