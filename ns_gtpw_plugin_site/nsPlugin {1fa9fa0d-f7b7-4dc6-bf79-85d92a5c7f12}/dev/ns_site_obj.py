import rhinoscriptsyntax as rs
import math

class site_obj(object):
    
    def __init__(self,O):
        self.site=O
        self.add_pts=[]
        self.pts=rs.DivideCurve(O,100)
        b=rs.BoundingBox(self.site)
        poly=rs.AddPolyline([b[0],b[1],b[2],b[3],b[0]])
        div=10
        u=int((b[1][0]-b[0][0])/div)
        v=int((b[2][1]-b[1][1])/div)
        for i in range(int(b[0][0]),int(b[1][0]),u):
            for j in range(int(b[1][1]),int(b[2][1]),v):
                p=[i,j,0]
                if(rs.PointInPlanarClosedCurve(p,self.site)!=0):
                    #self.add_pts.append(p)
                    self.pts.append(p)
        rs.DeleteObject(poly)
        
    def getPts(self):
        return self.pts
        
    def getAddPts(self):
        return self.add_pts
        
    def displayPts(self):
        u=0
        for i in self.pts:
            #rs.AddTextDot(str(u),i)
            u+=1
