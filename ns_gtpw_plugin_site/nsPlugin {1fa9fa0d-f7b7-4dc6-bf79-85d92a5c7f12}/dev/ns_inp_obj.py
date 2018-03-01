intx1=rs.CurveCurveIntersection(poly_geo,i)
                if(intx1 and len(intx1)>0):
                    sum+=1
            if(sum<1):
                rs.DeleteObject(poly_geo)
                return poly
            else:
                rs.DeleteObject(poly_geo)
                return None
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
    
    def getReqPoly(self):
        # internal poly - n in number same as boundary poly
        return self.req_poly
    
    def getGenPoly(self):
        #boundary poly - n in number 
        return self.gen_poly
    
    def setGenPoly(self,poly):
        self.gen_poly.append(poly)
    
    def checkContainment(self,a,b,c):
        t1=rs.PointInPlanarClosedCurve(a,self.crv)
        t2=rs.PointInPlanarClosedCurve(b,self.crv)
        t3=rs.PointInPlanarClosedCurve(c,self.crv)
        sum=0
        for i in self.neg_crv:
            tx1=rs.PointInPlanarClosedCurve(a,i)
            tx2=rs.PointInPlanarClosedCurve(b,i)
            tx3=rs.PointInPlanarClosedCurve(c,i)
            if(tx1==0 and tx2==0 and tx3==0):
                pass
                #point is outside curve 
            else:
                #point is inside curve 
                sum+=1

        if(t1!=0 and t2!=0 and t3!=0 and sum<1):
            return True #inside or on curve
        else:
            return False    #outside the curve
    
    def addSrf(self,srf):
        self.srf.append(srf)
        
    def getSrf(self):
        return self.srf
    
    def getColr(self):
        return self.colr
    
    def display(self):
        srfobj_li=[]
        for srf in self.srf:
            b=rs.BoundingBox(self.srf)            
            p0=b[0]
            p1=b[1]
            p2=b[2]
            p3=b[3]
            ht=str(rs.Distance(b[3],b[7]))

    def setFloorPlate(self, s):
        self.floor_plate=s
        
    def getFloorPlate(self):
        return self.floor_plate
