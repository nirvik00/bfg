import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter
from ns_inp_obj import inp_obj as inp_obj
from ns_site_obj import site_obj as site_obj

class main(object):
    def __init__(self,x,c):
        self.path=x
        self.site=rs.coercecurve(c)
        self.req_obj=[]
        self.site_ar=rs.CurveArea(self.site)[0]
        self.fsr=0
        self.bua=float(self.site_ar)*float(self.fsr)
        self.srf_obj=[]
            
    def getInpObj(self):
        ln=[]
        with open(self.path ,"r") as f:
            x=f.readlines() 
        rs.ClearCommandHistory()
        k=0
        r=[]
        req_total_far=0
        for i in x:
            if(k>0):
                try:
                    n=i.split(',')[0]
                    num=i.split(',')[1]
                    far_rat=float(i.split(',')[2])
                    req_total_far+=far_rat
                    l_min=i.split(',')[3]
                    l_max=i.split(',')[4]
                    w_min=i.split(',')[5]
                    w_max=i.split(',')[6]
                    h_min=i.split(',')[7]
                    h_max=i.split(',')[8]
                    sep_min=i.split(',')[9]
                    sep_max=i.split(',')[10]
                    colr=i.split(',')[11]
                    o=inp_obj(self.site,n,num,far_rat,l_min,l_max,w_min,w_max,h_min,h_max,sep_min,sep_max,colr)
                    r.append(o)
                except:
                    print('error in csv')
                    break
            k+=1
        self.fsr = req_total_far
        self.bua=float(self.site_ar)*float(self.fsr)
        for i in r:
            ar=i.getArea()
            num_flrs=int(ar/(i.getNumber()*i.getFloorArea()))+1
            i.setNumFloors(num_flrs)
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
            num_flrs=i.getNumFloors()
            l=i.getSide0()
            w=i.getSide1()
            a=i.getReqAr()
            h=i.getHt()
            #print(num_flrs, l, w, a, h)
            if((num_flrs*4)<(a/(2*l*w))):
                rs.MessageBox('number of floor = '+str(num_flrs)+'\ninput L and W for the required FSR are insufficient.\nCompensated in height ')
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
                        self.srf_obj.append([i,srf])
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
                    
    def finalSrf(self):
        return self.srf_obj
    
    def getMainFSR(self):
        return self.fsr
