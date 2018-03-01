import rhinoscriptsyntax as rs
import random
import math
import os
from time import time
from ns_inp_obj import inp_obj as inp_obj
from ns_main_2 import main as main
from ns_site_obj import site_obj as site_obj

class RunProc(object):
    def __init__(self):
        rs.AddLayer("garbage",visible=False)
        self.max=500
        self.fsr=0
        self.loc_pts=[]
        self.res_obj=[]
        self.del_srf_ite=[]
        self.del_flr_plate_ite=[]
        self.num_copies=1
        self.site_crv=rs.GetObject('pick site boundary')
        self.neg_site_crv=rs.GetObjects('pick negative boundary')
        self.ht_constraints=rs.GetObjects('pick height constraints')
        self.site_copy=[]
        self.req_srfobj_li=[]
        self.got_ar_li=[]
        n=rs.GetInteger('Enter number of variations required')
        if(n==0 or n==None):
            n=1
        FileName="input_1.csv"
        self.FilePath=rs.GetString("Enter the working directory for the program : ")
        if(self.FilePath==""):
            self.FilePath=os.getcwd()
        try:
            os.stat(self.FilePath)
        except:
            print('folder does not exist')
            return
        os.chdir(self.FilePath)
        req_fsr=3.0

        a=int(math.sqrt(n))
        b=int(math.sqrt(n))
        self.num_copies=n
        self.max=self.getMax()
        req_str_li=[]
        k=0
        rs.ClearCommandHistory()
        print('processing...')
        rs.EnableRedraw(False)
        self.req_srfobj_li=[]
        # this is the correct field
        for i in range(0,a,1):
            for j in range(0,b,1):
                BoolAR=False
                print('iteration %s in RunProc()'%(k))
                temp_site_crv=rs.CopyObject(self.site_crv,[self.max*i,self.max*j,0])
                self.site_copy.append(temp_site_crv)
                try:
                    temp_neg_crv=rs.CopyObjects(self.neg_site_crv,[self.max*i,self.max*j,0])
                except:
                    temp_neg_crv=None
                try:
                    temp_ht_constraints=rs.CopyObjects(self.ht_constraints,[self.max*i,self.max*j,0])
                except:
                    temp_ht_constraints=None
                m=main(FileName,temp_site_crv,temp_neg_crv,temp_ht_constraints)
                r=m.getInpObj()
                self.res_obj.append(r)
                got_flr_area_ite=m.genFuncObj_Site()
                self.got_ar_li.append(got_flr_area_ite)
                s=m.retResult()
                self.fsr=m.getMainFSR()
                
                ###   highlight or not
                pt=rs.CurveAreaCentroid(temp_site_crv)[0]
                self.loc_pts.append(pt)# =>same as: got_area=m.retGenArea()
                ### test for area satisfiaed
                ret_per_ar=self.getVar(got_flr_area_ite,s)
                if(ret_per_ar<10):
                    rs.AddCircle(pt, self.getMax()/2)
                
                #print("variation : ",ret_per_ar)
                msg=''
                if(ret_per_ar>5):
                    msg=("area not met")
                    BoolAR=False
                else:
                    BoolAR=True
                    msg=("area is met")
                #rs.MessageBox(msg)
                #print(msg)
                #end test
                req_str_li.append(s)
                
                for nli in self.res_obj:
                    for mli in nli:
                        mli.display()
                #three connections
                dx=pt[0]
                dy=pt[1]
                v=[dx,dy,0]
                srf_obj=m.finalSrf()
                #end 3 connections
                self.addLabel(k,temp_site_crv)
                self.req_srfobj_li.append(m.finalSrf())
                k+=1
        try:
            self.writeToCsv(k,req_str_li)
        except:
            pass
        rs.EnableRedraw(True)
    
    def getVar(self, ar, str_li):
        total_area=0
        gc=0
        site_area=rs.CurveArea(self.site_crv)[0]
        for j in str_li:#1-d element of str list
            #name, area, num_flrs, num_poly, total_ar_int_poly
            gc+=j[2]*j[4]
        bua=site_area*self.fsr
        f_gc=gc*100/site_area
        per_var_area=(math.fabs(bua-ar)*100)/(bua)
        return per_var_area
    
    def addLabel(self,k,crv):
        b=rs.BoundingBox(crv)
        rs.AddTextDot((k+1),b[0])
        
    def getMax(self):
        max=0
        crv_pts=rs.CurvePoints(self.site_crv)
        for i in range(len(crv_pts)):
            p0=crv_pts[i]
            for j in range(len(crv_pts)):
                p1=crv_pts[j]
                d=rs.Distance(p0,p1)
                if(d>max):
                    max=d
        return max
   
    def writeToCsv(self, counter, str_li):
        FilePath=self.FilePath
        try:
            os.stat(FilePath)
        except:
            print('1folder does not exist')
            return
        os.chdir(FilePath)
        file='output'+str(time())+".csv"
        fs=open(file,"w")
        site_area=rs.CurveArea(self.site_crv)[0]
        fs.write("\nSiteArea"+","+str(site_area))
        fs.write("\nF.S.R Required"+","+str(self.fsr))
        fs.write("\nBuilt-up Area Required"+","+str(site_area*self.fsr))
        best_ite=100
        best_index=0
        for i in range(counter):#2-d str list
            fs.write("\n\n\n,,ENTRY NUMBER,"+str(i+1))
            fs.write("\nType of Building,Required Area,Num of Each, Num plotted, Area of floorplate, Area Achieved, Balance\n")
            total_area=0
            gc=0
            for j in str_li[i]:#1-d element of str list
                #name, area, num_flrs, num_poly, ar_int_poly, actual_area_type
                fs.write(str(j[0])+","+str(j[1])+","+str(j[2])+","+str(j[3])+","+str(j[4])+","+str(j[5])+","+str(j[6])+"\n")
                total_area+=float(j[5])
                gc+=j[2]*j[4]
            fs.write("\nGross Floor Area,"+str(total_area))
            fsr=total_area/site_area
            fs.write("\nF.S.R,"+str(fsr))
            f_gc=gc*100/site_area
            fs.write("\nGround Coverage,"+str(f_gc))
            per_var_area = (math.fabs(total_area-(site_area*self.fsr)) * 100)/(site_area*self.fsr)
            fs.write("\nPercentage Variation in GFA ,"+str(per_var_area))
            this_ite=math.fabs(self.fsr-fsr)
            #print(this_ite)
            if(this_ite<best_ite):
                best_ite=this_ite
                best_index=i
        fs.close()
        r=self.res_obj[best_index]
        loc_pt=self.loc_pts[best_index]
        rs.AddCircle(loc_pt,(2+self.max)/2)


if __name__=='__main__':
    rs.ClearCommandHistory()
    RunProc()
        try:
            os.stat(self.FilePath)
        except:
            print('folder does not exist')
            return
        os.chdir(self.FilePath)
        req_fsr=3.0

        a=int(math.sqrt(n))
        b=int(math.sqrt(n))
        self.num_copies=n
        self.max=self.getMax()
        req_str_li=[]
        k=0
        rs.ClearCommandHistory()
        print('processing...')
        rs.EnableRedraw(False)
        self.req_srfobj_li=[]
        # this is the correct field
        for i in range(0,a,1):
            for j in range(0,b,1):
                BoolAR=False
                print('iteration %s in RunProc()'%(k))
                temp_site_crv=rs.CopyObject(self.site_crv,[self.max*i,self.max*j,0])
                self.site_copy.append(temp_site_crv)
                try:
                    temp_neg_crv=rs.CopyObjects(self.neg_site_crv,[self.max*i,self.max*j,0])
                except:
                    temp_neg_crv=None
                try:
                    temp_ht_constraints=rs.CopyObjects(self.ht_constraints,[self.max*i,self.max*j,0])
                except:
                    temp_ht_constraints=None
                m=main(FileName,temp_site_crv,temp_neg_crv,temp_ht_constraints)
                r=m.getInpObj()
                self.res_obj.append(r)
                got_flr_area_ite=m.genFuncObj_Site()
                self.got_ar_li.append(got_flr_area_ite)
                s=m.retResult()
                self.fsr=m.getMainFSR()
                
                ###   highlight or not
                pt=rs.CurveAreaCentroid(temp_site_crv)[0]
                self.loc_pts.append(pt)# =>same as: got_area=m.retGenArea()
                ### test for area satisfiaed
                ret_per_ar=self.getVar(got_flr_area_ite,s)
                if(ret_per_ar<10):
                    rs.AddCircle(pt, self.getMax()/2)
                
                #print("variation : ",ret_per_ar)
                msg=''
                if(ret_per_ar>5):
                    msg=("area not met")
                    BoolAR=False
                else:
                    BoolAR=True
                    msg=("area is met")
                #rs.MessageBox(msg)
                #print(msg)
                #end test
                req_str_li.append(s)
                
                for nli in self.res_obj:
                    for mli in nli:
                        mli.display()
                #three connections
                dx=pt[0]
                dy=pt[1]
                v=[dx,dy,0]
                srf_obj=m.finalSrf()
                #end 3 connections
                self.addLabel(k,temp_site_crv)
                self.req_srfobj_li.append(m.finalSrf())
                k+=1
        try:
            self.writeToCsv(k,req_str_li)
        except:
            pass
        rs.EnableRedraw(True)
    
    def getVar(self, ar, str_li):
        total_area=0
        gc=0
        site_area=rs.CurveArea(self.site_crv)[0]
        for j in str_li:#1-d element of str list
            #name, area, num_flrs, num_poly, total_ar_int_poly
            gc+=j[2]*j[4]
        bua=site_area*self.fsr
        f_gc=gc*100/site_area
        per_var_area=(math.fabs(bua-ar)*100)/(bua)
        return per_var_area
    
    def addLabel(self,k,crv):
        b=rs.BoundingBox(crv)
        rs.AddTextDot((k+1),b[0])
        
    def getMax(self):
        max=0
        crv_pts=rs.CurvePoints(self.site_crv)
        for i in range(len(crv_pts)):
            p0=crv_pts[i]
            for j in range(len(crv_pts)):
                p1=crv_pts[j]
                d=rs.Distance(p0,p1)
                if(d>max):
                    max=d
        return max
   
    def writeToCsv(self, counter, str_li):
        FilePath=self.FilePath
        try:
            os.stat(FilePath)
        except:
            print('1folder does not exist')
            return
        os.chdir(FilePath)
        file='output'+str(time())+".csv"
        fs=open(file,"w")
        site_area=rs.CurveArea(self.site_crv)[0]
        fs.write("\nSiteArea"+","+str(site_area))
        fs.write("\nF.S.R Required"+","+str(self.fsr))
        fs.write("\nBuilt-up Area Required"+","+str(site_area*self.fsr))
        best_ite=100
        best_index=0
        for i in range(counter):#2-d str list
            fs.write("\n\n\n,,ENTRY NUMBER,"+str(i+1))
            fs.write("\nType of Building,Required Area,Num of Each, Num plotted, Area of floorplate, Area Achieved, Balance\n")
            total_area=0
            gc=0
            for j in str_li[i]:#1-d element of str list
                #name, area, num_flrs, num_poly, ar_int_poly, actual_area_type
                fs.write(str(j[0])+","+str(j[1])+","+str(j[2])+","+str(j[3])+","+str(j[4])+","+str(j[5])+","+str(j[6])+"\n")
                total_area+=float(j[5])
                gc+=j[2]*j[4]
            fs.write("\nGross Floor Area,"+str(total_area))
            fsr=total_area/site_area
            fs.write("\nF.S.R,"+str(fsr))
            f_gc=gc*100/site_area
            fs.write("\nGround Coverage,"+str(f_gc))
            per_var_area = (math.fabs(total_area-(site_area*self.fsr)) * 100)/(site_area*self.fsr)
            fs.write("\nPercentage Variation in GFA ,"+str(per_var_area))
            this_ite=math.fabs(self.fsr-fsr)
            #print(this_ite)
            if(this_ite<best_ite):
                
                best_ite=this_ite
                best_index=i
        fs.close()
        r=self.res_obj[best_index]
        loc_pt=self.loc_pts[best_index]
        rs.AddCircle(loc_pt,(2+self.max)/2)


if __name__=='__main__':
    rs.ClearCommandHistory()
    RunProc()
