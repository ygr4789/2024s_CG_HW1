import numpy as np

class IK2Link:
    """
    Two link planar manipulator.
    Consider the case where the joint is angled downward.
    """
    def __init__(self, l1, l2):
        self._l1 = l1
        self._l2 = l2
        self._th1 = 0.0
        self._th2 = 0.0
        
    def set_target(self, x:float, y:float):
        l1 = self._l1
        l2 = self._l2
        r_sqr = x**2 + y**2
        c = ((l1**2+l2**2)-r_sqr)/(2*l1*l2)
        if c>1 or c<-1:
            if r_sqr > (l1+l2)**2:
                self._th1 = np.arctan2(y,x)
                self._th2 = 0.0
            if l2 > np.sqrt(r_sqr) + l1:
                self._th1 = np.pi + np.arctan2(y,x)
                self._th2 = np.pi
            if l1 > np.sqrt(r_sqr) + l2:
                self._th1 = np.arctan2(y,x)
                self._th2 = np.pi
            return
        alpha = np.arccos(c)
        self._th1 = np.arctan2(y,x) + np.arctan2(l2*np.sin(alpha),l1-l2*np.cos(alpha))
        self._th2 = alpha - np.pi
        
    @property
    def th1(self):
        return self._th1
        
    @property
    def th2(self):
        return self._th2

class SecondOrderDynamics:
    def __init__(self, f:float, z:float, r:float, x0):
        self._k1 = z/(np.pi*f)
        self._k2 = 1/((2*np.pi*f)**2)
        self._k3 = r*z/(2*np.pi*f)
        self._dt_crit = 0.8 * (np.sqrt(4*self._k2+self._k1**2)-self._k1)
        self._xp = x0 # previous input
        self._y = x0 # output position
        self._yd = None # output velocity
        
    def update(self, dt:float, x):
        xd = (x - self._xp) / dt
        if self._yd is None: self._yd = xd
        self._xp = x
        it = int(np.ceil(dt / self._dt_crit))
        dt /= it
        for i in range(it):
            self._y = self._y + self._yd * dt
            self._yd = self._yd + (x + xd*self._k3 - self._y - self._yd*self._k1) * dt/self._k2
            
    @property
    def y(self):
        return self._y
        
    @property
    def yd(self):
        return self._yd
    @yd.setter
    def yd(self, v):
        self._yd = v