import rhinoscript.userinterface
import rhinoscript.geometry
import rhinoscriptsyntax as rs
import file2 as proc

__commandname__ = "gensite"

def RunCommand( is_interactive ):
  p=proc.RunProc()
  printDetails()
  return 0
rs.ClearCommandHistory()

def printDetails():
    print "This is a site builder plugin created by Georgia Institute of Technology in association with Perkins and Will"
    print "Contact:\n\t1. Nirvik: nirviksaha@gatech.edu \n\t2. John: John.Haymaker@perkinswill.com \n\t3. Dennis: dennis.shelden@design.gatech.edu"

RunCommand(True)