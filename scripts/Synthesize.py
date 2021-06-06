import json
import os

def synthesize(args):

    ConfigFile = open(os.environ["HIBRIDA_CONFIG_FILE"], "r")
    ConfigDict = json.loads(ConfigFile.read())
    ProjectDir = ConfigDict["Projects"][args.ProjectName]["ProjectDir"]
    
    # Check if given project path exists
    if not os.path.isdir(ProjectDir):
        
        print("Error: ProjectDir <" + ProjectDir + "> does not exist")
        exit(1)
    
    if args.Tool == "Genus":

        # Set up environment vars
        os.environ["SynthProjectDir"] = ProjectDir
        os.environ["SynthVoltageLevel"] = args.Voltage
        os.environ["SynthProcessCorner"] = args.Process
        
        # Call genus
        #os.system("module add cdn/genus/genus181")
        os.system("module add cdn/genus/genus181; genus -log " + str(ProjectDir) + "/log/cadence/genus.log -f " + str(ProjectDir) + "/synthesis/scripts/Genus.tcl")
    
    if args.Tool == "RTLCompiler":

        # Set up environment vars
        os.environ["SynthProjectDir"] = ProjectDir
        os.environ["SynthVoltageLevel"] = args.Voltage
        os.environ["SynthProcessCorner"] = args.Process
        
        # Call genus
        #os.system("module add cdn/genus/genus181")
        os.system("module add cdn/rc/rc142; rc -log " + str(ProjectDir) + "/log/cadence/RTLCompiler.log -files " + str(ProjectDir) + "/synthesis/scripts/RTLCompiler.tcl")
    
    else:
    
        #print("Error: Tool <" + args.Tool + "> is not recognized")
        #exit(1)
        NotImplementedError
    
    ConfigDict["MostRecentProject"] = args.ProjectName
    ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
    ConfigFile.close()
    
    print("synthesize ran successfully!")
    
