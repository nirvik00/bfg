import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter

class inp_obj(object):
    #def __init__(self,c,fsr,n,a,d,e,s,num,max_ht,colr):
    def __init__(self,c,fsr,n,num,a_min,a_max,l_min,l_max,w_min,w_max,h_min,h_max,sep_min,sep_max,colr):
        self.name=n
        self.crv=c
        self.site_area=rs.CurveArea(c)[0]
        self.fsr=fsr
        self.bua=self.site_area*self.fsr
        self.num_floors=0
        self.gen_poly=[]
        self.req_poly=[]
        self.floor_plates=[]
        self.min_ht=h_min
        self.max_ht=h_max
        self.srf=[]
        re=int(colr.split("-")[0])
        gr=int(colr.split("-")[1])
        bl=int(colr.split("-")[2])
        self.colr=(re,gr,bl)
        self.ar_0=float(a_min)
        self.ar_1=float(a_max)
        self.d0_0=float(l_min)
        self.d0_1=float(l_max)
        self.d1_0=float(w_min)
        self.d1_1=float(w_max)
        self.s_0=float(sep_min)
        self.s_1=float(sep_max)
        self.number=int(num)
        self.ar=random.randint(int(self.ar_0),int(self.ar_1))
        self.d0=random.randint(int(self.d0_0),int(self.d0_1))
        self.d1=random.randint(int(self.d1_0),int(self.d1_1))
        self.sep=random.randint(int(self.s_0),int(self.s_1))
        self.b0=self.d0+self.sep
        self.b1=self.d1+self.sep
        
    def getName(self):
        return self.name
        
    def getArea(self):
        return self.ar
        
    def getSide0(self):
        return self.d0
        
    def getSide1(self):
        return self.d1
        
    def getSep(self):
        return self.sep
        
    def getB0(self):
        return self.b0
        
    def getB1(self):
        return self.b1
        
    def getNumber(self):
        return self.number
        
    def setNumber(self,num):
        self.number=num
        
    def setNumFloors(self,num):
        self.num_floors=num
    
    def getFloorArea(self):
        ar=self.d1*self.d0
        return ar
    
    def getNumFloors(self):
        return self.num_floors
    
    def getCrvArea(self):
        ar=0
        for i in self.getReqPoly():
            ar+=rs.CurveArea(i)[0]
        return ar
    
    def getTotalArea(self):
        ar=rs.CurveArea(self.getReqPoly()[0])[0]*self.getNumFloors()
        return ar
        
    def getConfig1(self,p,q,r):
        pr=rs.VectorUnitize(rs.VectorCreate(r,p))
        prN=rs.VectorScale(rs.VectorRotate(pr,90,[0,0,1]),self.b0)
        prA=rs.VectorScale(pr,self.b1)
        a=rs.PointAdd(q,prA)  # goes from q to a along pr
        b=rs.PointAdd(q,prN)  # goes from q to b perpendicular to pr
        c=rs.PointAdd(b,prA)
        t=self.checkContainment(a,b,c)
        if(t==True):
            #poly=rs.AddPolyline([q,a,c,b,q])
            poly=[q,a,c,b,q]
            return poly
        else:
            return None
    
    def genIntPoly(self, poly):
        cen=rs.CurveAreaCentroid(poly)[0]
        pts=rs.CurvePoints(poly)
        a=[(pts[0][0]+pts[1][0])/2,(pts[0][1]+pts[1][1])/2,0]
        b=[(pts[0][0]+pts[3][0])/2,(pts[0][1]+pts[3][1])/2,0]
        vec1=rs.VectorScale(rs.VectorUnitize(rs.VectorCreate(cen,a)),self.d0/2)
        vec2=rs.VectorScale(rs.VectorUnitize(rs.VectorCreate(cen,b)),self.d1/2)
        p=rs.PointAdd(cen,vec1)
        q=rs.PointAdd(cen,-vec1)
        r=rs.PointAdd(p,vec2)
        u=rs.PointAdd(p,-vec2)
        t=rs.PointAdd(q,vec2)
        s=rs.PointAdd(q,-vec2)
        poly=rs.AddPolyline([r,u,s,t,r])
        self.req_poly.append(poly)
    
    def getReqPoly(self):# internal poly - n in number same as boundary poly
        return self.req_poly
    
    def getGenPoly(self):#boundary poly - n in number 
        return self.gen_poly
    
    def setGenPoly(self,poly):
        self.gen_poly.append(poly)
    
    def checkContainment(self,a,b,c):
        t1=rs.PointInPlanarClosedCurve(a,self.crv)
        t2=rs.PointInPlanarClosedCurve(b,self.crv)
        t3=rs.PointInPlanarClosedCurve(c,self.crv)
        if(t1!=0 and t2!=0 and t3!=0):
            return True
        else:
            return False
    
    def addSrf(self,srf):
        self.srf.append(srf)
        
    def getSrf(self):
        return self.srf
    
    def getColr(self):
        return self.colr
    
    def display(self):
        print('attributes are ok for the class ns_inp_obj')
    
