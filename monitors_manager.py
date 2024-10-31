from screeninfo import get_monitors
from dataclasses import dataclass, asdict
import typing as T

@dataclass
class KMSMonitor:
    x: int
    y: int
    width: int
    height: int
    name: str = None
    width_mm: T.Optional[int] = None
    height_mm: T.Optional[int] = None
    is_primary: T.Optional[bool] = None
    is_distant: T.Optional[bool] = None

    def __repr__(self) -> str:
        return (
            f"KMSMonitor("
            f"x={self.x}, y={self.y}, "
            f"width={self.width}, height={self.height}, "
            f"width_mm={self.width_mm}, height_mm={self.height_mm}, "
            f"name={self.name!r}, "
            f"is_primary={self.is_primary}, "
            f"is_distant={self.is_distant}"
            f")"
        )


# Monitor geometry functions
def check_is_in(p, m:KMSMonitor):
    """ Check if a point (tuple) is inside a monitor """
    return p[0]>=m.x and p[0]<m.x + m.width and p[1]>=m.y and p[1]<m.y + m.height

def min_dist_to_monitor(p, m:KMSMonitor):
    """ Get the minimal distance between a point (tuple) and a monitor """
    return min([max(abs(p[0]-m.x), abs(p[1]-m.y)), max(abs(p[0]-(m.x+m.width-1)), abs(p[1]-(m.y+m.height-1)))])

def project_to(p, m:KMSMonitor):
    """ Project a point (tuple) to it's closest position on a monitor (must be in) """
    (x,y) = p
    if( x < m.x ):
        x = m.x
    elif( x >= m.x+m.width ):
        x = m.x+m.width-1
    if( y < m.y ):
        y = m.y
    elif( y >= m.y+m.height ):
        y = m.y+m.height-1
    return (x,y)

class MonitorsManager():
    def __init__(self) -> None:
        self.monitors = {}
        self.primary = None
        self.update_monitors()

    def update_monitors(self):
        for m in get_monitors():
            km = KMSMonitor(**asdict(m))
            km.is_distant=False
            self.monitors[m.name] = km

        tst = KMSMonitor(x=-1920,y=0,width=1920, height=1080, name='TestMonitor', is_distant = True)
        self.monitors[tst.name] = tst

        self.primary = [m for m in self.monitors.values() if m.is_primary][0]

    def __repr__(self) -> str:
        return '\n'.join([str(m) for m in self.monitors.values()])
    
    def get_monitor(self, p):
        """Get the monitor including the given point (tuple). None if outside all."""
        inside = [m for m in self.monitors.values() if check_is_in(p, m)]
        return None if len(inside) == 0 else inside[0]

    def project_to_closest(self, p, monitors=None):
        """ Project a point (tuple) to the closest monitor"""
        monitors = list(self.monitors.values()) if monitors is None else monitors
        distances = [min_dist_to_monitor(p,m) for m in monitors]
        closest = distances.index(min(distances))
        return project_to(p, monitors[closest]), monitors[closest]
    
    def project_to_closest_local(self, p, monitors=None):
        return self.project_to_closest(p, [m for m in self.monitors.values() if not m.is_distant])

