import rhinoscriptsyntax as rs
import random
import math
import os
from time import time
from ns_site_obj import site_obj as site_obj
from ns_inp_obj import inp_obj as inp_obj
from ns_genSite import genSite as genSite
#from ns_main import main as main
from ns_main_2 import main as main

class RunProc(object):
    def __init__(self):
        rs.AddLayer("garbage",visible=False)
        self.max=500
        self.fsr=3
        self.loc_pts=[]
        self.res_obj=[]
        self.num_copies=1
        self.site_crv=rs.GetObject('pick site boundary')
        self.site_copy=[]
        FileName="input.csv"
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
        """
        # since total area for each function is given, fsr required is not applicable
        try:
            self.fsr=float(rs.GetString("Enter FSR required"))
        except:
            print('this is incorrect data type default value of fsr=3.0 assumed')
        """
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
        
        # this is the correct field
        for i in range(0,a,1):
            for j in range(0,b,1):
                print('iteration %s in RunProc()'%(k))
                temp_site_crv=rs.CopyObject(self.site_crv,[self.max*i,self.max*j,0])
                self.site_copy.append(temp_site_crv)
                m=main(FileName,self.fsr,temp_site_crv)
                r=m.getInpObj()
                self.res_obj.append(r)
                m.genFuncObj_Site()
                s=m.retResult()
                req_str_li.append(s)
                pt=rs.CurveAreaCentroid(temp_site_crv)[0]
                self.loc_pts.append(pt)
                self.addLabel(k,temp_site_crv)
                k+=1
        try:
            self.writeToCsv(k,req_str_li)
        except:
            pass
        # end of correct code block
        
        # start of revised code block
        """
        for i in range(0,a,1):
            for j in range(0,b,1):
                print('iteration %s in RunProc()'%(k))
                temp_site_crv=self.site_crv#rs.CopyObject(self.site_crv,[self.max*i,self.max*j,0])
                self.site_copy.append(temp_site_crv)
                m=main(FileName,self.fsr,temp_site_crv)
                r=m.getInpObj()
                self.res_obj.append(r)
                m.genFuncObj_Site()
                s=m.retResult()
                req_str_li.append(s)
                pt=rs.CurveAreaCentroid(temp_site_crv)[0]
                self.loc_pts.append(pt)
                self.addLabel(k,temp_site_crv)
                rs.RenderColor(1,(255,255,255))
                str_img=str(k+1)+'.png'
                rs.Redraw()
                #rs.Command("_ViewCaptureToFile",tr_img)
                rs.CreatePreviewImage(str_img, "Perspective", (1200,1024), 4, False)
                print('img created')
                m.delResult()
                k+=1
        self.writeToCsvPcp(k,req_str_li)
        """
        #end of revised code block
        
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
                #name, area, num_flrs, num_poly, ar_int_poly
                #fs.write(str(j[0])+","+str(j[1])+","+str(j[2])+","+str(j[3])+","+str(j[4])+"\n")
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
        file='output'+str(time())+".csv"
        fs=open(file,"a")
        site_area=rs.CurveArea(self.site_crv)[0]
        fs.write("\nSiteArea"+","+str(site_area))
        fs.write("\nF.S.R Required"+","+str(self.fsr))
        fs.write("\nBuilt-up Area Required"+","+str(site_area*self.fsr))
        best_ite=100
        best_index=0
        for i in range(counter):#2-d str list
            fs.write("\n\n\n,,ENTRY NUMBER,"+str(i+1))
            fs.write("\nType of Building,Total Area,Num of floors, Num plotted, Area of floorplate\n")
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
            this_ite=math.fabs(self.fsr-fsr)
            #print(this_ite)
            if(this_ite<best_ite):
                best_ite=this_ite
                best_index=i
        fs.close()
        print(best_index,best_ite)
        r=self.res_obj[best_index]
        loc_pt=self.loc_pts[best_index]
        rs.AddCircle(loc_pt,self.max/2)
        #rs.AddTextDot(best_index,loc_pt)
        #print(len(self.res_obj))
        
        """
        res_obj=self.res_obj[best_index]
        pt=rs.CurveAreaCentroid(self.site_crv)[0]
        for i in res_obj:
            print(i.getName())
            rs.CopyObject(i.getSrf(),[-self.max*self.num_copies,0,0])
        req_site_crv=self.site_copy[best_index+1]
        req_site_cen=rs.CurveAreaCentroid(req_site_crv)[0]
        #rs.CopyObject(req_site_crv,[-self.max*self.num_copies,0,0])
        """

if __name__=='__main__':
    RunProc()