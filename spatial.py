"""Frame-local broad phase; exact swept collision remains in GameSession."""
import math

class EnemyGrid:
    size=160
    def __init__(self,enemies):
        self.cells={};self.locations={};self.radius=max((e.radius for e in enemies),default=0)
        for enemy in enemies:self.move(enemy)
    def move(self,enemy):
        cell=(math.floor(enemy.pos.x/self.size),math.floor(enemy.pos.y/self.size))
        old=self.locations.get(enemy.uid)
        if cell==old:return
        if old is not None:self.cells[old].pop(enemy.uid,None)
        self.locations[enemy.uid]=cell;self.cells.setdefault(cell,{})[enemy.uid]=enemy
    def query(self,minx,miny,maxx,maxy):
        extra=self.radius
        for y in range(math.floor((miny-extra)/self.size),math.floor((maxy+extra)/self.size)+1):
            for x in range(math.floor((minx-extra)/self.size),math.floor((maxx+extra)/self.size)+1):
                yield from self.cells.get((x,y),{}).values()
    def clear(self):self.cells.clear();self.locations.clear()
