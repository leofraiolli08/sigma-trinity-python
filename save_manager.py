import json
import logging
import math
import os
import tempfile
from pathlib import Path
from settings import BASE_DIR, CHARACTERS, SCREEN_SHAKE_ENABLED
from progression import META, ACHIEVEMENTS

UNLOCK_REQUIREMENTS=('leo','guxta','zatex')
FUSION_REQUIREMENTS=(*UNLOCK_REQUIREMENTS,'davi','leozauxta')
SAVE_CHARACTERS=tuple(dict.fromkeys((*CHARACTERS,'zato')))

def defaults():
    return dict(bestiary=[],clip_seen=[],challenge_records={},telemetry={},high_score=0,best_time=0,highest_level=1,boss_defeated=False,coins=0,meta={},achievements=[],visited=[],lifetime_kills=0,mission_stats={},best_wave=0,
                plays={k:0 for k in SAVE_CHARACTERS},wins={k:0 for k in SAVE_CHARACTERS},secret_clears=[],fusion_offered=False,
                settings=dict(volume=.45,music_volume=.35,fullscreen=False,shake=SCREEN_SHAKE_ENABLED,numbers=True,flashes=True,short_cinema=True,effects='full'))
class SaveManager:
    def __init__(self,path=None):
        self.path=Path(path) if path is not None else BASE_DIR/'save.json'; self.data=defaults(); self.warning=''
        self.backup=self.path.with_suffix(self.path.suffix+'.bak')
        try:
            raw=self.read_saved()
            for k in ('high_score','best_time','highest_level'):
                v=raw.get(k)
                if type(v) is int and v>=0:self.data[k]=min(v,10**12)
                elif type(v) is float and math.isfinite(v) and v>=0:self.data[k]=min(v,10**12)
            self.data['boss_defeated']=raw.get('boss_defeated') is True
            for key in ('coins','lifetime_kills','best_wave'):
                v=raw.get(key,0)
                if type(v) is int and v>=0:self.data[key]=min(v,10**12)
            meta=raw.get('meta',{})
            if isinstance(meta,dict):
                for key,spec in META.items():
                    v=meta.get(key,0)
                    if type(v) is int:self.data['meta'][key]=max(0,min(spec[2],v))
            from maps import MAPS
            for key,allowed in (('achievements',ACHIEVEMENTS),('visited',MAPS)):
                values=raw.get(key,[])
                if isinstance(values,list):self.data[key]=list(dict.fromkeys(v for v in values if isinstance(v,str) and v in allowed))
            for table in ('plays','wins'):
                values=raw.get(table,{})
                if isinstance(values,dict):
                    for k in SAVE_CHARACTERS:
                        v=values.get(k,0)
                        if type(v) is int and v>=0: self.data[table][k]=v
            for table in ('plays','wins'):
                self.data[table]['zatex']=max(self.data[table]['zatex'],self.data[table]['zato'])
            clears=raw.get('secret_clears',[])
            if isinstance(clears,list):self.data['secret_clears']=[k for k in ('leozauxta','leozauxtaci') if k in clears]
            # Preserve secrets that were actually played in earlier releases.
            if 'secret_clears' not in raw:
                self.data['secret_clears']=[k for k in ('leozauxta','leozauxtaci') if self.data['plays'][k]>0 or self.data['wins'][k]>0]
            self.data['fusion_offered']=raw.get('fusion_offered') is True
            values=raw.get('mission_stats',{})
            if isinstance(values,dict):
                for key in ('kills','chests','transforms','wave','victories'):
                    v=values.get(key,0)
                    if type(v) is int and v>=0:self.data['mission_stats'][key]=v
            self.data['mission_stats']['kills']=max(self.data['mission_stats'].get('kills',0),self.data['lifetime_kills'])
            values=raw.get('bestiary',[])
            allowed={f'{theme}:{i}' for theme in MAPS for i in range(7)}
            if isinstance(values,list):self.data['bestiary']=list(dict.fromkeys(v for v in values if isinstance(v,str) and v in allowed))
            values=raw.get('clip_seen',[])
            if isinstance(values,list):self.data['clip_seen']=list(dict.fromkeys(v for v in values if isinstance(v,str) and len(v)<96))[:256]
            from expedition import RULES
            records=raw.get('challenge_records',{})
            if isinstance(records,dict):self.data['challenge_records']={k:v for k,v in records.items() if k in RULES and type(v) is int and 0<=v<=1000000}
            metrics=raw.get('telemetry',{})
            if isinstance(metrics,dict):self.data['telemetry']={k:v for k,v in metrics.items() if k in ('first_form','boss_seconds') and type(v) in (int,float) and math.isfinite(v) and 0<=v<=1e7}
            opts=raw.get('settings',{})
            if isinstance(opts,dict):
                if opts.get('effects') in ('full','balanced','low'):self.data['settings']['effects']=opts['effects']
                for k in ('fullscreen','shake','numbers','flashes','short_cinema'):
                    if type(opts.get(k)) is bool: self.data['settings'][k]=opts[k]
                for key in ('volume','music_volume'):
                    v=opts.get(key)
                    if type(v) in (int,float) and math.isfinite(v): self.data['settings'][key]=max(0,min(1,v))
        except FileNotFoundError: pass
        except (OSError,ValueError,OverflowError) as exc:
            self.warning='Save inválido ou indisponível; padrões carregados.'; logging.warning('%s %s',self.warning,exc)
    def read_saved(self):
        try:
            raw=json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw,dict):raise ValueError('Save não é objeto')
            return raw
        except (OSError,ValueError) as original:
            try:
                raw=json.loads(self.backup.read_text(encoding='utf-8'))
                if not isinstance(raw,dict):raise ValueError('Backup inválido')
                self.warning='Progresso recuperado do backup automático.'
                return raw
            except (OSError,ValueError):raise original
    def unlock_progress(self):
        return {key:self.data['wins'].get(key,0)>0 for key in UNLOCK_REQUIREMENTS}
    def is_unlocked(self,key):
        if key not in CHARACTERS:return False
        requirements=UNLOCK_REQUIREMENTS if key=='leozauxta' else FUSION_REQUIREMENTS if key=='leozauxtaci' else ()
        eligible=all(self.data['wins'].get(k,0)>0 or (k=='zatex' and self.data['wins'].get('zato',0)>0) for k in requirements)
        return eligible and (not requirements or key in self.data['secret_clears'])
    def challenge_available(self,key):
        requirements=UNLOCK_REQUIREMENTS if key=='leozauxta' else FUSION_REQUIREMENTS if key=='leozauxtaci' else ()
        return bool(requirements) and not self.is_unlocked(key) and all(self.data['wins'].get(k,0)>0 or (k=='zatex' and self.data['wins'].get('zato',0)>0) for k in requirements)
    def visible_characters(self):return [k for k in CHARACTERS if self.is_unlocked(k)]
    def save(self):
        temp=None;backup_temp=None
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            blob=json.dumps(self.data,indent=2,ensure_ascii=False,allow_nan=False)
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=self.path.parent,prefix=self.path.name+'.',suffix='.tmp',delete=False) as stream:
                temp=Path(stream.name);stream.write(blob);stream.flush();os.fsync(stream.fileno())
            if self.path.exists():
                current=self.path.read_bytes()
                try:valid=isinstance(json.loads(current),dict)
                except (ValueError,UnicodeError):valid=False
                if valid:
                    with tempfile.NamedTemporaryFile(dir=self.path.parent,prefix=self.path.name+'.backup.',suffix='.tmp',delete=False) as stream:
                        backup_temp=Path(stream.name);stream.write(current);stream.flush();os.fsync(stream.fileno())
                    backup_temp.replace(self.backup)
                else:
                    # Retain a corrupted original for recovery instead of deleting it.
                    with tempfile.NamedTemporaryFile(dir=self.path.parent,prefix=self.path.name+'.corrompido.',suffix='.json',delete=False) as stream:stream.write(current)
            temp.replace(self.path)
            if self.warning=='Não foi possível salvar os recordes.':self.warning=''
            return True
        except (OSError,ValueError,TypeError) as exc:
            self.warning='Não foi possível salvar os recordes.'; logging.warning('%s %s',self.warning,exc); return False
        finally:
            for leftover in (temp,backup_temp):
                if leftover and leftover.exists():
                    try:leftover.unlink()
                    except OSError:pass
    def record(self,session,victory,finished=True):
        d=self.data; p=session.player
        d['clip_seen']=sorted(set(d['clip_seen'])|p.clip_seen)[:256]
        d['bestiary']=sorted(set(d['bestiary'])|session.discovered)
        d['telemetry']={k:session.telemetry[k] for k in ('first_form','boss_seconds')}
        if not session.challenge:d['challenge_records'][session.run_rule]=max(d['challenge_records'].get(session.run_rule,0),session.waves.completed)
        if session.challenge:
            if victory and not session.victory_paid:
                if session.challenge not in d['secret_clears']:d['secret_clears'].append(session.challenge)
                d['coins']+=100;session.reward+=100;session.victory_paid=True
            return self.save()
        d['most_used']=max(d['plays'],key=d['plays'].get)
        d['high_score']=max(d['high_score'],session.kills*100+p.level*50+int(session.time))
        d['best_time']=max(d['best_time'],round(session.time,2)); d['highest_level']=max(d['highest_level'],p.level)
        d['boss_defeated'] |= victory
        if victory and not session.victory_paid:d['wins'][p.key]+=1;session.victory_paid=True
        d['best_wave']=max(d['best_wave'],session.waves.completed)
        from progression import checkpoint
        checkpoint(d,session,victory,finished)
        return self.save()
