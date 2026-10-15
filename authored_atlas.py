"""Isolate actual silhouettes before scaling; grid lines are not crop boundaries.

AI-authored poses can extend beyond their nominal cell. Find bodies across the
whole row so a wide punch is not truncated or attached to its neighbor.
"""
import statistics
import pygame as pg

def poses(sheet, rows, cols=8, heights=None, group_rows=1):
    width, height = sheet.get_size()
    parsed=[];result=[]
    for row in range(rows):
        top, bottom=round(row*height/rows),round((row+1)*height/rows)
        strip=sheet.subsurface((0,top,width,bottom-top)).copy()
        components=pg.mask.from_surface(strip,96).connected_components(100)
        bodies=sorted(sorted(components,key=lambda m:m.count(),reverse=True)[:cols],
                      key=lambda m:m.get_bounding_rects()[0].centerx)
        if len(bodies)!=cols:raise ValueError(f'Atlas: {len(bodies)} corpos na linha {row}; esperado {cols}')
        cells=[];boxes=[]
        for body in bodies:
            box=body.get_bounding_rects()[0]
            cell=strip.subsurface(box).copy()
            matte=body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
            cell.blit(matte.subsurface(box),(0,0),special_flags=pg.BLEND_RGBA_MULT)
            cells.append(cell);boxes.append(box)
        parsed.append((cells,boxes))
    for first in range(0,rows,group_rows):
        cells=[cell for row in parsed[first:first+group_rows] for cell in row[0]]
        boxes=[box for row in parsed[first:first+group_rows] for box in row[1]]
        native=(heights or [54]*rows)[first]
        factor=native/statistics.median(b.height for b in boxes[:min(4,cols)])
        canvas_size=(round(max(b.width for b in boxes)*factor)+8,
                     round(max(b.height for b in boxes)*factor)+8)
        frames=[]
        for cell in cells:
            scaled=pg.transform.scale(cell,(max(1,round(cell.get_width()*factor)),max(1,round(cell.get_height()*factor))))
            frame=pg.Surface(canvas_size,pg.SRCALPHA)
            frame.blit(scaled,((canvas_size[0]-scaled.get_width())//2,canvas_size[1]-3-scaled.get_height()))
            frames.append(frame)
        for at in range(0,len(frames),cols):result.append(frames[at:at+cols])
    return result
