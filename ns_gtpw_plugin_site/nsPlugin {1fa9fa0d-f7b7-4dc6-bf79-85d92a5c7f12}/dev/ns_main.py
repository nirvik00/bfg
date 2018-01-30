import rhinoscriptsyntax as rs
import math
import random
from time import time
import operator
from operator import itemgetter
from ns_site_obj import site_obj as site_obj
from ns_inp_obj import inp_obj as inp_obj
from ns_genSite import genSite as genSite

class main(object):
    def __init__(self,x,c):
        self.path=x
        self.site=c
        self.req_obj=[]
        self.site_ar=rs.CurveArea(self.site)[0]
        #print('area: ',self.site_ar)
    def getInpObj(self):
        ln=[]
        with open(self.path ,"r") as f:
            x=f.readlines()
        k=0
        r=[]
        for i in x:
            if(k>0):
                n=i.split(',')[0]
                a=i.split(',')[1]
                d0=i.split(',')[2]
                d1=i.split(',')[3]
                s=i.split(',')[4]
                num=i.split(',')[5]
                o=inp_obj(self.site,n,a,d0,d1,s,num)
                r.append(o)
            k+=1
        for i in r:
            ar=i.getArea()
            num=int(ar/(i.getNumber()*i.getFloorArea()))
            i.setNumFloors(num)
            print('req : ',i.getName(),ar,i.getNumber(),i.getFloorArea(),i.getArea(), num)
        self.req_obj=r
        return r
    def checkPoly(self,pts,poly):
        sum=0
        for i in pts:
            m=rs.PointInPlanarClosedCurve(i,poly)
            if(m!=0):
                sum+=1
        poly2=rs.AddPolyline(pts)
        pts2=rs.CurvePoints(poly)
        for i in pts2:
            m=rs.PointInPlanarClosedCurve(i,poly2)
            if(m!=0):
                sum+=1
        intx=rs.CurveCurveIntersection(poly,poly2)
        rs.DeleteObject(poly2)
        if(sum>0 or intx):
            return False
        else:
            return True
    def genFuncObj_Site(self):
        s=site_obj(self.site)
        pts=s.getPts()
        s.displayPts()
        poly_list=[]
        for i in self.req_obj:
            for j in range(i.getNumber()):
                obj=i
                T=False
                k=0
                this_gen_poly=None
                while(T==False and k<50):
                    x=random.randint(1,len(pts)-2)
                    p=pts[x-1]
                    q=pts[x]
                    r=pts[x+1]
                    poly=obj.getConfig1(p,q,r)
                    sum=0
                    if(poly is not None and len(poly)>0):
                        sum=0
                        if(poly_list and len(poly_list)>0):
                            for m in poly_list:
                                polyY=rs.AddPolyline(m)
                                G=self.checkPoly(poly,polyY)
                                rs.DeleteObject(polyY)
                                if(G==False):
                                    sum+=1
                                    break
                            if(sum==0):
                                T=True
                                if(poly not in poly_list):
                                    this_gen_poly=poly
                                    poly_list.append(poly)
                        elif(poly is not None and len(poly)>0):
                            if(poly not in poly_list):
                                this_gen_poly=poly
                                poly_list.append(poly)
                    k+=1
                if(this_gen_poly is not None):
                    i.setGenPoly(rs.AddPolyline(this_gen_poly))
        for i in self.req_obj:
            poly=i.getGenPoly()
            for j in poly:
                i.genIntPoly(j)
                npoly=i.getReqPoly()
                for k in range(i.getNumFloors()):
                    rs.CopyObjects(npoly,[0,0,4*k])
                pass
    def writeToCsv(self):
        suffix='output'+str(time())+".csv"
        file=suffix
        fs=open(file,"a")
        fs.write("\n\nentry number,"+str(time())+"\n\n")
        fs.write("\nSiteArea"+","+str(rs.CurveArea(self.site)[0]))
        fs.write("\n\n\nobjects,NAME,AREA,NUM OF FLOORS,NUMBER OF FOOTPRINTS,TOTAL AREA OCC")
        sum_area=0
        sum_foot=0
        for i in self.req_obj:
            total_area=i.getNumFloors()*rs.CurveArea(i.getReqPoly()[0])[0]
            sum_foot+=i.getCrvArea()
            sum_area+=i.getTotalArea()
            #print('area of floor=',rs.CurveArea(i.getReqPoly()[0])[0])
            fs.write("\nObjects"+","+str(i.getName())+","+str(i.getArea())+","+str(i.getNumFloors())+","+str(len(i.getGenPoly()))+","+str(total_area))
        fs.write("\n\n\ntotal footprint"+","+str(sum_foot))
        fs.write("\n\n\ntotal area occupied"+","+str(sum_area))
        fs.close()
