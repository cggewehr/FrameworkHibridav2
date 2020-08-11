
def projgen(args):
    
    import os
    
    # Check if given project path exists. If not, mkdir
    if os.path.isdir(args.ProjectDirectory + "/" + args.ProjectName):
        
        while True:
        
            print("Warning: Project path <" + args.ProjectDirectory + "/" + args.ProjectName + "> already exists. Do you wish to proceed (Y/N)?")
            ipt = raw_input()
            
            if ipt == "Y" or ipt == "y":
                break
            elif ipt == "N" or ipt == "n":
                exit(0)
                
    else:
        
        os.makedirs(args.ProjectDirectory + "/" + args.ProjectName)
        
    # Makes "log", "flow" and "platform" dirs
    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/flow")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/log")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/platform")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/src_json")
    except OSError:
        pass

    # TODO: Copy testbench HDL to project directory, in order to have project directory as reference directory in simulation tool
    
    # os.environ["MOST_RECENT_HIBRIDA_PROJECT"] = args.ProjectDirectory + "/" + args.ProjectName

    print("Created \"" + args.ProjectName + "\" at \"" + args.ProjectDirectory + "\"")
    