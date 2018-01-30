import rhinoscriptsyntax as rs

class genSite(object):
    
    def __init__(self,a,b):
        p=[]
        m=2
        n=2
        p.append([a+0,b+0,0])
        p.append([a+600*m,b+0,0])
        p.append([a+600*m,b+300*n,0])
        p.append([a+300*m,b+300*n,0])
        p.append([a+300*m,b+600*n,0])
        p.append([a+0,b+600*n,0])
        p.append([a+0,b+0,0])
        self.site=rs.AddPolyline(p)
        
    def getSite(self):
        return self.site
