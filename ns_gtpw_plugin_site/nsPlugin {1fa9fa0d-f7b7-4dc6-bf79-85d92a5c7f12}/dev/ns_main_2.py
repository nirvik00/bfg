import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter
from ns_inp_obj import inp_obj as inp_obj
from ns_site_obj import site_obj as site_obj

class main(object):
    def __init__(self,x,c,nc,hc,srf=None):
        self.neg_site_crv=nc
        self.ht_constraints=hc
        self.site_srf=srf
        self.path=x
        self.site=rs.coercecurve(c)
        self.req_obj=[]
        self.site_ar=rs.CurveArea(self.site)[0]
        self.fsr=0
        self.bua=float(self.site_ar)*float(self.fsr)
        self.srf_obj=[]
        self.floor_plate=[]
        self.total_floor_area=0
        self.highlight=False
        self.generation_area=0
    
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
                    if(n=="" or not n):
                        break
                    num=i.split(',')[1]
                    far_rat=float(i.split(',')[2])
                    req_total_far+=float(far_rat)
                    l_min=i.split(',')[3]
                    l_max=i.split(',')[4]
                    w_min=i.split(',')[5]
                    w_max=i.split(',')[6]
                    h_=i.split(',')[7]
                    sep_min=i.split(',')[8]
                    sep_max=i.split(',')[9]
                    colr=i.split(',')[10]
                    o=inp_obj(self.site,n,num,far_rat,l_min,l_max,w_min,w_max,h_,sep_min,sep_max,colr,self.neg_site_crv)
                    r.append(o)
                except:
                    #print('error in csv')
                    break
            k+=1
        self.fsr = req_total_far
        self.bua=float(self.site_ar)*float(self.fsr)
        for i in r:
            ar=i.getArea()
            num_flrs=int(ar/(i.getNumber()*i.getFloorArea()))
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
    
    def getHtConstraintsData(self, check_for_poly):
        j=check_for_poly
        ht_constraint=1000000
        min_ht=ht_constraint
        if(self.ht_constraints):
            for h_ite in self.ht_constraints:
                bhtc=rs.BoundingBox(h_ite)
                poly_htc=rs.AddPolyline([bhtc[0],bhtc[1],bhtc[2],bhtc[3],bhtc[0]])
                int_htcon_sum=0 #if this remains 0 => no change
                for poly_pt in rs.CurvePoints(j):
                    t=rs.PointInPlanarClosedCurve(poly_pt,poly_htc)
                    if(t!=0): #point not outside poly
                        int_htcon_sum+=1
                for bound_pt in rs.CurvePoints(poly_htc):
                    t=rs.PointInPlanarClosedCurve(bound_pt,j)
                    if(t!=0): #point not outside poly
                        int_htcon_sum+=1
                intx1=rs.CurveCurveIntersection(poly_htc,j)
                if(intx1 and len(intx1)>0):
                    int_htcon_sum+=1
                if(int_htcon_sum>0):
                    ht_constraint=rs.Distance(bhtc[0],bhtc[4])
                    if(ht_constraint<min_ht):
                        min_ht=ht_constraint
                else:
                    pass
                rs.DeleteObject(poly_htc)
        return min_ht
    
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
                while(T==False and k<500):
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
                        if(self.site_srf ==None):
                            i.setGenPoly(rs.AddPolyline(this_gen_poly))#boundary-poly
                        else:
                            poly=rs.AddPolyline(this_gen_poly)#boundary-poly
                            topo_poly=self.constructTopoPoly(self.site_srf,poly)
                            i.setGenPoly(topo_poly)#boundary-poly
        counter=0
        floor_plate=[]
        self.total_floor_area=0
        for i in self.req_obj:
            num_flrs=i.getNumFloors()
            l=i.getSide0()
            w=i.getSide1()
            a=i.getReqAr()
            h=i.getHt()
            n=i.getNumber()
            nm=i.getName()
            poss_num_flrs=(h/4)*n
            poly=i.getGenPoly() # n boundary poygons are created from input
            #print(nm,l,w,h,n,a,' :: ',num_flrs, poss_num_flrs)
            actual_num_flr=0
            actual_ar_each=0
            if(poly is not None and len(poly)>0):
                for j in poly: # for each poly in bounding-poly get internal-poly
                    counter2=0
                    i.genIntPoly(j) # iterate over the first poly then second, this time there are 2 polys
                    npoly=i.getReqPoly()
                for j in i.getReqPoly():
                    ####         handle height constraint elements      ####
                    ht_constraint=self.getHtConstraintsData(j)
                    """
                    ht_constraint=[]
                    if(self.ht_constraints):
                        for h_ite in self.ht_constraints:
                            bhtc=rs.BoundingBox(h_ite)
                            poly_htc=rs.AddPolyline([bhtc[0],bhtc[1],bhtc[2],bhtc[3],bhtc[0]])
                            int_htcon_sum=0 #if this remains 0 => no change
                            for poly_pt in rs.CurvePoints(j):
                                t=rs.PointInPlanarClosedCurve(poly_pt,poly_htc)
                                if(t!=0): #point not outside poly
                                    int_htcon_sum+=1
                            for bound_pt in rs.CurvePoints(poly_htc):
                                t=rs.PointInPlanarClosedCurve(bound_pt,j)
                                if(t!=0): #point not outside poly
                                    int_htcon_sum+=1
                            intx1=rs.CurveCurveIntersection(poly_htc,j)
                            if(intx1 and len(intx1)>0):
                                int_htcon_sum+=1
                            if(int_htcon_sum>0):
                                ht_constraint=rs.Distance(bhtc[0],bhtc[4])
                                #print('height constraint applied',nm)
                            else:
                                #print('height constraint NOT applied',nm)
                                pass
                            rs.DeleteObject(poly_htc)
                    """
                    li=[]
                    for k in range(i.getNumFloors()+1):
                        """
                        # stop iteration at height input csv
                        if((4*k)>h):
                            break
                        """
                        # allow iteration until area is met
                        # stop iteration at height constraint
                        if((4*k)>ht_constraint):
                            break
                        c=rs.CopyObjects(j,[0,0,4*k])
                        self.total_floor_area+=rs.CurveArea(j)[0]
                        if(rs.IsCurve(c)):
                            floor_plate.append(c)
                            actual_num_flr+=1
                            actual_ar_each+=(rs.CurveArea(c)[0])
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
                i.setActualNumFlrs(actual_num_flr)
                i.setActualArea(actual_ar_each)
        self.floor_plate=floor_plate
        #rs.CopyObjects(self.floor_plate, [300,0,0])
        #print("total floor area = ", self.total_floor_area)
        return self.total_floor_area
    
    def constructTopoPoly(self,srf,poly):
        if(srf ==None):
            return
        poly_pts=rs.CurvePoints(poly)
        pts=poly_pts
        req_pts=[]
        req_pts_dup=[]
        for i in pts:
            pt2=rs.AddPoint([i[0],i[1],i[2]-1000])
            L=rs.AddLine(i,pt2)
            intx=rs.CurveSurfaceIntersection(L,srf)
            if(intx and len(intx)>0):
                pt=[intx[0][1][0],intx[0][1][1],intx[0][1][2]]
                rs.DeleteObject(L)
                rs.DeleteObject(pt2)
                req_pts.append([pt[0],pt[1],pt[2]])
                req_pts_dup.append([pt[0],pt[1],pt[2]])
        req_pts_dup.sort(key=operator.itemgetter(2))
        max_z=req_pts_dup[len(req_pts_dup)-1][2]# higher
        min_z=req_pts_dup[0][2]# higher
        high_pts=[]
        low_pts=[]
        for i in req_pts:
            high_pt=[i[0],i[1],max_z]
            high_pts.append(high_pt)
            low_pt=[i[0],i[1],min_z]
            low_pts.append(low_pt)
        high_pl=rs.AddPolyline(high_pts)
        low_pl=rs.AddPolyline(low_pts)
        this_srf=rs.AddLoftSrf([high_pl,low_pl])
        rs.DeleteObjects([low_pl,poly])
        rs.CapPlanarHoles(this_srf)
        return high_pl
    
    def retResult(self):
        str=[]
        sum_area=0
        sum_foot=0
        req_str=[]
        self.generation_area=0
        for i in self.req_obj:
            name=i.getName()
            area=i.getArea()
            #num_flrs=i.getNumFloors()
            #num_flrs=i.getPossFlrFromHt()
            num_flrs=i.getActualNumFlrs()
            num_poly=len(i.getGenPoly())
            actual_area=i.getActualArea()
            self.generation_area+=actual_area
            #find the area of internal poly
            num_int_poly_check=len(i.getReqPoly())
            int_poly=[]
            ar_int_poly=0
            try:
                int_poly=i.getReqPoly()[0]
                ar_int_poly=rs.CurveArea(int_poly)[0]
            except:
                pass
            diff_area=i.getDifferenceArea()
            #print / add as string
            this_str=[name, area, (num_poly), (num_flrs), ar_int_poly, actual_area, diff_area]
            #print(name, area, num_poly, num_flrs, ar_int_poly, diff_area)
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
    
    def retGenArea(self):
        return self.generation_area
    
    def finalSrf(self):
        return self.srf_obj
    
    def finalFloorPlate(self):
        return self.floor_plate
    
    def getMainFSR(self):
        return self.fsr
