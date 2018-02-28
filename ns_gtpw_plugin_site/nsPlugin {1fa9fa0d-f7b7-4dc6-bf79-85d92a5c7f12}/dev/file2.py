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
        self.num_copies=1
        self.site_crv=rs.GetObject('pick site boundary')
        self.site_copy=[]
        self.req_srfobj_li=[]
        FileName="input_1.csv"
        FilePath=rs.GetString("Enter the working directory for the program : ")
        if(FilePath==""):
            FilePath='c:/nir_dev/temp/output_1'
        try:
            os.stat(FilePath)
        except:
            print('folder does not exist')
            return
        os.chdir(FilePath)
        req_fsr=3.0
        n=rs.GetInteger('Enter number of variations required')
        if(n==0 or n==None):
            n=1
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
                print('iteration %s in RunProc()'%(k))
                temp_site_crv=rs.CopyObject(self.site_crv,[self.max*i,self.max*j,0])
                self.site_copy.append(temp_site_crv)
                m=main(FileName,temp_site_crv)
                r=m.getInpObj()
                self.res_obj.append(r)
                m.genFuncObj_Site()
                s=m.retResult()
                self.fsr=m.getMainFSR()
                req_str_li.append(s)
                pt=rs.CurveAreaCentroid(temp_site_crv)[0]
                self.loc_pts.append(pt)
                for nli in self.res_obj:
                    for mli in nli:
                        mli.display()                
                #three connections
                dx=pt[0]
                dy=pt[1]
                v=[dx,dy,0]
                srf_obj=m.finalSrf()
                if(n==1):
                    self.output3sync(srf_obj,rs.CurvePoints(temp_site_crv),v,k)
                else:
                    self.output3mass(srf_obj,rs.CurvePoints(temp_site_crv),v,k)
                FilePath=FilePath='c:/nir_dev/temp/output_1'
                os.chdir(FilePath)
                #end 3 connections
                self.addLabel(k,temp_site_crv)
                self.req_srfobj_li.append(m.finalSrf())
                k+=1
        
        self.writeToCsv(k,req_str_li)
        rs.EnableRedraw(True)
        
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
    
    def writeToCsvPcp(self, counter, str_li):
        FilePath='c:/nir_dev/temp/output_1'
        try:
            os.stat(FilePath)
        except:
            print('2folder does not exist')
            return        
        file='output'+str(time())+".csv"
        fs=open(file,"a")
        site_area=rs.CurveArea(self.site_crv)[0]
        fs.write("Run Id,GFA,FSR,Ground Coverage,Num of Floors, Num Plotted, Area of Floor Plate, Image (PNG)\n")
        for i in range(counter):#2-d str list
            total_area=0
            gc=0
            num_flrs=0
            num_plot=0
            area_plate=0
            for j in str_li[i]:#1-d element of str list
                total_area+=j[2]*j[3]*j[4]
                gc+=j[2]*j[4]
                num_flrs+=(j[1])
                num_plot+=(j[3])
                area_plate+=(j[4])
            run_id=i+1
            gfa=total_area
            gc=gc*100/site_area
            fsr=total_area/site_area
            img=str(i+1)+'.png'
            fs.write(str(run_id)+","+str(gfa)+","+str(fsr)+","+str(gc)+","+str(num_flrs)+","+str(num_plot)+","+str(area_plate)+","+img+"\n")
        fs.close()

    def writeToCsv(self, counter, str_li):
        FilePath='c:/nir_dev/temp/output_1'
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
            fs.write("\nType of Building,Total Area,Num of Each, Num plotted, Area of floorplate\n")
            total_area=0
            gc=0
            for j in str_li[i]:#1-d element of str list
                #name, area, num_flrs, num_poly, ar_int_poly
                fs.write(str(j[0])+","+str(j[1])+","+str(j[2])+","+str(j[3])+","+str(j[4])+"\n")
                total_area+=j[2]*j[3]*j[4]
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
        rs.AddCircle(loc_pt,self.max/2)
        
        
    def output3sync(self, srf_obj,pts,v,k):
        FilePath='c:/nir_dev/web/dennis/proj1/public/csv'
        try:
            os.stat(FilePath)
        except:
            print('0folder does not exist')
            return
        os.chdir(FilePath)
        try:
            os.remove('output3.csv')
        except OSError:
            pass
        file='output3'+".csv"
        fs=open(file,"w")
        site_pts=[]
        p=""
        for i in pts:
            x=i[0]-v[0]
            y=i[1]-v[1]
            p+=(str(x)+";"+str(y)+",")
        fs.write(p)
        fs.write("\n")
        s=[] 
        geo_di={}
        for i in srf_obj:
            j=i[0].getName()
            srf=i[1]
            b=rs.BoundingBox(srf)
            x=b[0][0]-v[0]
            y=b[0][1]-v[1]
            z=0
            l=rs.Distance(b[0],b[1])
            w=rs.Distance(b[1],b[2])
            h=rs.Distance(b[3],b[7])
            str0=j+","+str(x)+","+str(y)+","+str(z)+","+str(l)+","+str(w)+","+str(h)
            s.append(str0)
            fs.write(str0)
            fs.write("\n")
        fs.close()
        
    def output3mass(self, srf_obj,pts,v,k):
        FilePath='c:/nir_dev/spatial_allocation/bfg_output/csv'
        try:
            os.stat(FilePath)
        except:
            print('0folder does not exist')
            return
        os.chdir(FilePath)
        try:
            os.remove('output3.csv')
        except OSError:
            pass
        file='output'+str(k)+".csv"
        fs=open(file,"w")
        site_pts=[]
        p=""
        for i in pts:
            x=i[0]-v[0]
            y=i[1]-v[1]
            p+=(str(x)+";"+str(y)+",")
        fs.write(p)
        fs.write("\n")
        s=[] 
        geo_di={}
        for i in srf_obj:
            j=i[0].getName()
            srf=i[1]
            b=rs.BoundingBox(srf)
            x=b[0][0]-v[0]
            y=b[0][1]-v[1]
            z=0
            l=rs.Distance(b[0],b[1])
            w=rs.Distance(b[1],b[2])
            h=rs.Distance(b[3],b[7])
            str0=j+","+str(x)+","+str(y)+","+str(z)+","+str(l)+","+str(w)+","+str(h)
            s.append(str0)
            fs.write(str0)
            fs.write("\n")
        fs.close()


if __name__=='__main__':
    RunProc()
