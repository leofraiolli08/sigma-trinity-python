"""Arena-specific AI art with deterministic pixel silhouettes as offline fallback."""
import pygame as pg

def figure(theme,kind,frame,boss=False):
    s=pg.Surface((64,80),pg.SRCALPHA);d=pg.draw;shift=frame*2;ink=(14,18,25)
    color={'city':(113,151,178),'ring':(176,116,88),'walls':(168,126,103),'fog':(116,101,160)}[theme]
    light=tuple(min(255,v+38) for v in color)
    x=32;y=29;wide=18 if kind in (3,5) else 13
    if theme=='city':
        if kind==4:
            d.polygon(s,ink,[(3,24),(25,18),(32,11),(40,18),(61,24),(49,36),(15,36)])
            d.polygon(s,color,[(6,25),(26,23),(32,15),(38,23),(58,25),(47,32),(17,32)])
            d.rect(s,(255,152,77),(27,23,10,4));d.rect(s,light,(7,27,13,2));d.rect(s,light,(44,27,13,2))
        else:
            d.rect(s,ink,(x-wide-2,y-2,wide*2+4,32));d.rect(s,color,(x-wide,y,wide*2,28))
            for xx in (x-13,x+4):
                d.rect(s,ink,(xx,55,10,20));d.rect(s,color,(xx+2,55,6,16-shift));d.rect(s,light,(xx,72-shift,12,4))
            d.rect(s,ink,(22,9,20,21));d.rect(s,color,(24,11,16,15));d.rect(s,(95,239,224),(25,16,14,3))
            for yy in range(34,48,4):d.rect(s,ink,(25,yy,14,2))
            for sign in (-1,1):
                xx=x+sign*(wide+5);d.rect(s,ink,(xx-4,31-shift,9,24));d.rect(s,light,(xx-2,33-shift,5,16))
            if kind in (1,5):d.rect(s,ink,(46,25,7,30));d.rect(s,(230,156,69),(48,26,3,14))
    elif theme=='ring':
        d.rect(s,ink,(x-wide-1,27,wide*2+2,28));d.rect(s,color,(x-wide,28,wide*2,22))
        d.rect(s,(42,37,58),(x-wide,49,wide*2,11));d.rect(s,(216,189,122),(x-wide,49,wide*2,3))
        for xx in (x-12,x+4):
            d.rect(s,color,(xx,59,8,12));d.rect(s,ink,(xx-2,68-shift,13,8));d.rect(s,(207,203,182),(xx-1,68-shift,10,2))
        d.rect(s,ink,(23,7,18,23));d.rect(s,color,(25,9,14,18));d.rect(s,(46,34,39),(23,7,18,5))
        d.rect(s,(250,217,152),(26,17,4,2));d.rect(s,(250,217,152),(35,17,4,2))
        for xx,yy in ((11,33-shift),(44,24+shift)):
            d.rect(s,ink,(xx-2,yy-2,13,17));d.rect(s,(164,49+kind*9,63),(xx,yy,10,13));d.rect(s,(230,204,170),(xx,yy+11,10,3))
        if kind==5:d.rect(s,(196,155,83),(21,7,23,4))
    elif theme=='walls':
        # Long-limbed giants, with exposed muscle plates and distinct proportions.
        d.polygon(s,ink,[(19,26),(43,26),(48,49),(41,57),(40,75),(31,75),(28,59),(22,75),(13,75),(21,51),(15,40)])
        d.polygon(s,color,[(20,28),(41,28),(45,48),(37,56),(37,72),(32,72),(29,54),(24,55),(20,72),(16,72),(24,48),(18,40)])
        for yy in (34,40,46):d.line(s,(116,66,59),(25,yy),(36,yy),2)
        d.rect(s,ink,(24,6,18,24));d.rect(s,color,(25,9,15,18))
        d.rect(s,(41,33,35),(23,5,20,8+kind%3));d.rect(s,(213,224,157),(27,16,4,2));d.rect(s,(213,224,157),(35,16,4,2))
        d.line(s,(244,219,185),(28,24),(38,24),2)
        for sign in (-1,1):
            xx=32+sign*17;d.line(s,ink,(xx,29),(xx+sign*7,56-shift),8);d.line(s,color,(xx,29),(xx+sign*7,56-shift),5)
        if kind in (3,5):
            for xx in (19,35):d.rect(s,(200,179,139),(xx,28,9,10));d.rect(s,light,(xx,29,7,2))
    else:
        # Masked lantern cultists and floating many-limbed shadows.
        d.polygon(s,ink,[(31,9),(46,32),(53,70),(39,64),(31,77),(21,65),(9,70),(18,31)])
        d.polygon(s,color,[(31,13),(42,32),(46,65),(35,61),(30,72),(24,61),(15,64),(22,32)])
        d.rect(s,(22,21,36),(24,23,17,17));d.rect(s,(222,215,188),(28,24,10,12))
        d.rect(s,(74,62,99),(30,28,2,3));d.rect(s,(74,62,99),(35,28,2,3))
        for i in range(3):d.line(s,(163,139,205),(25+i*6,43),(19+i*10,63-shift),1)
        d.line(s,light,(18,37),(7,47-shift),3);d.rect(s,(215,174,106),(3,44-shift,8,11));d.rect(s,(250,220,152),(5,47-shift,4,5))
        if kind in (2,4):
            for i in range(4):d.lines(s,color,False,[(32,52),(8+i*14,66+shift),(4+i*16,73)],3)
    if boss:
        d.polygon(s,(232,197,119),[(19,7),(18,0),(26,4),(32,0),(38,4),(46,0),(44,7)])
        return pg.transform.scale(s,(112,140))
    return s

def load(root=None,status=None):
    images={};logical={}
    for theme in ('city','ring','walls','fog'):
        if status is not None:status[theme]='fallback'
        for kind in range(6):
            for frame in range(2):
                key=f'{theme}_enemy_{kind}_{frame}';images[key]=figure(theme,kind,frame);logical[key]=(48,60) if theme!='walls' else (65,81)
        for frame in range(2):
            key=f'{theme}_boss_{frame}';images[key]=figure(theme,5,frame,True);logical[key]=(100,125)
    if root is not None:
        for theme in ('city','ring','walls','fog'):
            path=root/'art'/f'{theme}_monsters.png'
            if not path.exists():continue
            try:sheet=pg.image.load(str(path)).convert_alpha()
            except (pg.error,OSError):continue
            w,h=sheet.get_size();cw,ch=w//4,h//2
            loaded=0
            for i in range(8):
                cell=sheet.subsurface((i%4*cw,i//4*ch,cw,ch)).copy()
                box=cell.get_bounding_rect(min_alpha=24)
                if not box.width or not box.height:continue
                src=cell.subsurface(box).copy()
                height=(112 if i>=6 else 44 if i==4 else 76 if theme=='walls' else 64 if i==3 else 58)
                width=max(1,round(src.get_width()*height/src.get_height()))
                im=pg.transform.scale(src,(width,height))
                for frame in range(2) if i<6 else (i-6,):
                    canvas=pg.Surface((width+4,height+4),pg.SRCALPHA)
                    canvas.blit(im,(2,2+frame if i<6 else 2))
                    name=f'{theme}_enemy_{i}_{frame}' if i<6 else f'{theme}_boss_{frame}'
                    images[name]=canvas;logical[name]=canvas.get_size()
                loaded+=1
            if status is not None and loaded==8:status[theme]='generated'
    return images,logical
