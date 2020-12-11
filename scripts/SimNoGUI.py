import json
import os

def simNoGUI(args):

    ConfigFile = open(os.environ["HIBRIDA_CONFIG_FILE"], "r")
    ConfigDict = json.loads(ConfigFile.read())
    ProjectDir = ConfigFile["Projects"][args.ProjectName]["ProjectDir"]
    
    # Check if given project path exists
    if not os.path.isdir(ProjectDir):
        
        print("Error: ProjectDir <" + ProjectDir + "> does not exist")
        exit(1)
    
    if args.Tool == "cadence":
        
        # Check if makefile exists
        if not os.path.isfile(os.path.join(ProjectDir, "makefile")):
        
            print("Error: Makefile does not exist for project <" + args.ProjectName + ">")
            print("Did you run projgen for another tool? To compile/elab/sim with with Cadence tools you must run projgen with Tool set as \"cadence\".")
        
        # Runs makefile with simnogui rule
        os.system("make -f " + os.path.join(ProjectDir, args.ProjectName) + " makefile simnogui")
        
    elif args.Tool == "vivado":
        
        # Runs vivado with simnogui script
        TCLScript = os.path.join(ConfigDict["HibridaPath"], "scripts", "vivado", "simnogui.tcl")
        TCLArgs = args.ProjectName + " " + ProjectDir
        os.system("vivado -mode batch -source " + TCLScript + " -tclargs " + TCLArgs)
        
    else:
    
        print("Error: Tool <" + args.Tool + "> is not recognized")
        exit(1)
    
    print("simNoGUI ran successfully!")
    ConfigFile.close()
    