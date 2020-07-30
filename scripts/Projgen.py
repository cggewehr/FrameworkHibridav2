
def projgen(args):
    
    import os
    import sys
    
    # Check if given project path exists. If not, mkdir
    if os.path.isdir(args.ProjectDirectory + "/" + args.ProjectName):
        
        while True:
        
            print("Warning: Project path <" + args.ProjectDirectory + "/" + args.ProjectName + "> already exists. Do you wish to proceed (Y/N)?")
            ipt = input()
            
            if ipt == "Y" or ipt == "y":
                break
            elif ipt == "N" or ipt == "n":
                exit(0)
                
    else:
        
        os.makedirs(args.ProjectDirectory + "/" + args.ProjectName)
        
    # Makes log and flow dirs
    os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/flow")
    os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/log")
    
    