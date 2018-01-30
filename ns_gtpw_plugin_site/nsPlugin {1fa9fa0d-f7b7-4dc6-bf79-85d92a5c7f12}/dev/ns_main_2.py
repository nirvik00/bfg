import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter
from ns_site_obj import site_obj as site_obj
from ns_inp_obj import inp_obj as inp_obj
from ns_genSite import genSite as genSite

class main(object):
    def __init__(self,x,fsr,c):
        self.path=x
        self.fsr=fsr
        self.site=c
        self.req_obj=[]
        self.site_ar=rs.CurveArea(self.site)[0]
        self.bua=float(self.site_ar)*float(self.fsr)
        #print('bua : ',self.bua)
            
    def getInpObj(self):
        ln=[]
        with open(self.path ,"r") as f:
            x=f.readlines()
        k=0
        r=[]
        for i in x:
            if(k>0):
                n=i.split(',')[0]
                num=i.split(',')[1]
                a_min=i.split(',')[2]
                a_max=i.split(',')[3]
                l_min=i.split(',')[4]
                l_max=i.split(',')[5]
                w_min=i.split(',')[6]
                w_max=i.split(',')[7]
                h_min=i.split(',')[8]
                h_max=i.split(',')[9]
                sep_min=i.split(',')[10]
                sep_max=i.split(',')[11]
                colr=i.split(',')[12]
                o=inp_obj(self.site,self.fsr,n,num,a_min,a_max,l_min,l_max,w_min,w_max,h_min,h_max,sep_min,sep_max,colr)
                r.append(o)
            k+=1
        for i in r:
            ar=i.getArea()
            num_flrs=int(ar/(i.getNumber()*i.getFloorArea()))+1
            i.setNumFloors(num_flrs)
            #print('req : ',i.getName(),ar,i.getNumber(),i.getFloorArea(),i.getArea(), num_flrs)
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
                while(T==False and k<100):
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
                    if(len(this_gen_poly)>0):
                        i.setGenPoly(rs.AddPolyline(this_gen_poly))#boundary-poly
        counter=0
        for i in self.req_obj:
            poly=i.getGenPoly() # n boundary poygons are created from input
            if(poly is not None and len(poly)>0):
                for j in poly: # for each poly in bounding-poly get internal-poly
                    counter2=0
                    i.genIntPoly(j) # iterate over the first poly then second, this time there are 2 polys
                    npoly=i.getReqPoly()
                for j in i.getReqPoly():
                    li=[]
                    for k in range(i.getNumFloors()):
                        c=rs.CopyObjects(j,[0,0,4*k])
                        rs.ObjectLayer(c,"garbage")
                        li.append(c)
                    try:
                        srf=rs.AddLoftSrf(li)
                        rs.CapPlanarHoles(srf)
                        rs.ObjectColor(srf,i.getColr())
                        i.addSrf(srf)
                    except:
                        pass
    def retResult(self):
        str=[]
        sum_area=0
        sum_foot=0
        req_str=[]
        for i in self.req_obj:
            name=i.getName()
            area=i.getArea()
            num_flrs=i.getNumFloors()
            num_poly=len(i.getGenPoly())
            #find the area of internal poly
            num_int_poly_check=len(i.getReqPoly())
            int_poly=[]
            ar_int_poly=0
            try:
                int_poly=i.getReqPoly()[0]
                ar_int_poly=rs.CurveArea(int_poly)[0]
            except:
                pass
            #print / add as string
            this_str=[name, area, num_poly, num_flrs, ar_int_poly]
            req_str.append(this_str)
        return req_str
    
    def delResult(self):
        for i in self.req_obj:
            srf=i.getSrf()
            try:
                rs.DeleteObjects(srf)
            except:
                try:
                    rs.DeleteObjects(srf)
                except:
                    pass
            int_poly=i.getReqPoly()
            try:
                rs.DeleteObjects(int_poly)
            except:
                try:
                    rs.DeleteObject(int_poly)
                except:
                    pass
            bound_poly=i.getGenPoly()
            try:
                rs.DeleteObjects(bound_poly)
            except:
                try:
                    rs.DeleteObject(bound_poly)
                except:
                    pass
                