#!/usr/bin/python
import argparse
import json
import sys
import os

# Imports command frontend scripts
import AddSearchPath
import Projgen
import SetConfig
import Flowgen
import Comp
import Elab
import Sim
import SimNoGUI
import Run
import RunNoGUI
import Synthesize
import LogParser

if os.getenv("HIBRIDA_NAME") is None:
    print("Error: Environment variable $HIBRIDA_NAME doesnt exist. Did you source/call the .source/.bat file created by the setup script?")
    exit(1)
    
# Reads config.json file for framework config parameters
ConfigFile = open(os.getenv("HIBRIDA_CONFIG_FILE"))
ConfigDict = json.loads(ConfigFile.read())

parser = argparse.ArgumentParser(prog = os.getenv("HIBRIDA_NAME"))
subparsers = parser.add_subparsers(title = "Hibrida subcommands")

# addSearchPath args
parser_addSearchPath = subparsers.add_parser("addSearchPath", help = "Adds a directory where files passed as arguments to setConfig command can be searched for")
parser_addSearchPath.set_defaults(func=AddSearchPath.addSearchPath)
parser_addSearchPath.add_argument("-alo", "--AllocationMapsPath", nargs = "+", help = "Adds a directory where Allocation Map JSON files will also be looked for in", type = str)
parser_addSearchPath.add_argument("-app", "--ApplicationsPath", nargs = "+", help = "Adds a directory where Applications JSON files will also be looked for in", type = str)
parser_addSearchPath.add_argument("-clo", "--ClusterClocksPath", nargs = "+", help = "Adds a directory where Cluster Clocks JSON files will also be looked for in", type = str)
parser_addSearchPath.add_argument("-top", "--TopologiesPath", nargs = "+", help = "Adds a directory where Topologies JSON files will also be looked for in", type = str)
parser_addSearchPath.add_argument("-wor", "--WorkloadsPath", nargs = "+", help = "Adds a directory where Workloads JSON files will also be looked for in", type = str)
# TODO: Add argument where search paths are printed out

# projgen args
parser_projgen = subparsers.add_parser("projgen", help = "Creates a new project at a given directory")
parser_projgen.set_defaults(func=Projgen.projgen)
parser_projgen.add_argument("-pd", "--ProjectDirectory", "--projdir",  type = str, default = ConfigDict["DefaultProjDir"])
parser_projgen.add_argument("-pn", "--ProjectName", "--projname", type = str, default = "HibridaProject")
parser_projgen.add_argument("-a", "--AppendName", "--appendname", help = "Appends ProjectName to ProjectDir path", action = "store_true", default = None)
supportedTools = ["cadence", "vivado", "Genus", "RTLCompiler"]
parser_projgen.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "Genus")

# TODO: Create project from topology .json file
#parser_projgen.add_argument("-f", "--TopologyFile", type = str, default = None)

# setConfig args
parser_setConfig = subparsers.add_parser("setConfig", help = "Sets AllocationMap/ClusterClocks/Topology/Workloads config files for a given project")
parser_setConfig.set_defaults(func=SetConfig.setConfig)
parser_setConfig.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, default = None)
parser_setConfig.add_argument("-a", "-alo", "--AllocationMapFile", "--allocationmapfile", help = "Allocation Map json file to be assotiated to given project", type = str)
parser_setConfig.add_argument("-c", "-clk", "--ClusterClocksFile", "--clusterclocksfile", help = "Cluster Clocks json file to be assotiated to given project", type = str)
parser_setConfig.add_argument("-t", "-top", "--TopologyFile", "--topologyfile", help = "Topology json file to be assotiated to given project", type = str)
parser_setConfig.add_argument("-w", "-wrk", "--WorkloadFile", "--workloadfile", help = "Workload json file to be assotiated to given project", type = str)
parser_setConfig.add_argument("-s", "--state", help = "Displays which AllocationMap/ClusterClocks/Topology/Workloads config files have been assotiated with given project", action = "store_true")

# flowgen args
parser_flowgen = subparsers.add_parser("flowgen", help = "Generates injector JSON config files, implementing a given workload in a given topology running at given clocks frequencies")
parser_flowgen.set_defaults(func=Flowgen.flowgen)
parser_flowgen.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, default = None, help = "Name of target project")

# compile args
parser_compile = subparsers.add_parser("compile", help = "Compiles HDL source files with a given tool")
parser_compile.set_defaults(func=Comp.comp)
parser_compile.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be compiled", default = None)
supportedTools = ["cadence", "vivado"]
parser_compile.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_compile.add_argument("-opt", type = str, help = "Additional options to VHDL compiler", default = "")

# elab args
parser_elab = subparsers.add_parser("elab", help = "Elaborates top level entity after compilation step")
parser_elab.set_defaults(func=Elab.elab)
parser_elab.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be elaborated", default = None)
supportedTools = ["cadence", "vivado"]
parser_elab.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_elab.add_argument("-opt", type = str, help = "Additional options to elaborator", default = "")

# sim args
parser_sim = subparsers.add_parser("sim", help = "Simulates project with waveform viewer")
parser_sim.set_defaults(func=Sim.sim)
parser_sim.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be simulated", default = None)
supportedTools = ["cadence", "vivado"]
parser_sim.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_sim.add_argument("-opt", type = str, help = "Additional options to simulator", default = "")

# simnogui args
parser_simnogui = subparsers.add_parser("simnogui", help = "Simulates project without waveform viewer")
parser_simnogui.set_defaults(func=SimNoGUI.simNoGUI)
parser_simnogui.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be simulated", default = None)
supportedTools = ["cadence", "vivado"]
parser_simnogui.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_simnogui.add_argument("-opt", type = str, help = "Additional options to simulator", default = "")

# run args
parser_run = subparsers.add_parser("run", help = "Compiles, elaborates and simulates project with waveform viewer")
parser_run.set_defaults(func=Run.run)
parser_run.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be simulated", default = None)
supportedTools = ["cadence", "vivado"]
parser_run.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_run.add_argument("-compopt", type = str, help = "Additional options to VHDL compiler", default = "")
parser_run.add_argument("-elabopt", type = str, help = "Additional options to elaborator", default = "")
parser_run.add_argument("-simopt", type = str, help = "Additional options to simulator", default = "")

# runnogui args
parser_runnogui = subparsers.add_parser("runnogui", help = "Compiles, elaborates and simulates project without waveform viewer")
parser_runnogui.set_defaults(func=RunNoGUI.runnogui)
parser_runnogui.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be simulated", default = None)
supportedTools = ["cadence", "vivado"]
parser_runnogui.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for compiling, elaborating and simulating project", default = "cadence")
parser_runnogui.add_argument("-compopt", type = str, help = "Additional options to VHDL compiler", default = "")
parser_runnogui.add_argument("-elabopt", type = str, help = "Additional options to elaborator", default = "")
parser_runnogui.add_argument("-simopt", type = str, help = "Additional options to simulator", default = "")

# synthesize args
parser_synthesize = subparsers.add_parser("synthesize", help = "Synthesizes project")
parser_synthesize.set_defaults(func=Synthesize.synthesize)
parser_synthesize.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project to be synthesized", default = None)
supportedTools = ["RTLCompiler", "Genus", "Vivado"]
parser_synthesize.add_argument("-t", "--Tool", "--tool", choices = supportedTools, type = str, help = "Tool used for synthesizing project", default = "Genus")
parser_synthesize.add_argument("-ve", "--Version", "--version", choices = supportedTools, type = str, help = "Version of tool used for synthesizing project", default = "181")
parser_synthesize.add_argument("-pr", "--Process", "--process", help = "Process corner", required = True)
parser_synthesize.add_argument("-vo", "--Voltage", "--voltage", help = "Voltage corner", required = True)
parser_synthesize.add_argument("-te", "--Temperature", "--temperature", help = "Temperature corner", required = True)

# logparser args
parser_logparser = subparsers.add_parser("logparser", help = "Analyzes log generated by simulation and informs performance parameters such as average latency")
parser_logparser.set_defaults(func=LogParser.logparser)
parser_logparser.add_argument("-p", "-pn", "--ProjectName", "--projname", type = str, help = "Name of project whose logs will be analyzed", default = None)
parser_logparser.add_argument("-PE", action = "store_true", help = "Perform analysis at PE level")
parser_logparser.add_argument("-t", "--Thread", "--thread", action = "store_true", help = "Perform analysis at Thread level")
parser_logparser.add_argument("-DVFS", action = "store_true", help = "Perform operating frequency analysis from DVFS service packets")
parser_logparser.add_argument("-min", "--MinimumOutputTimestamp", type = int, help = "Minimum output timestamp time (in ns)", default = 0)
parser_logparser.add_argument("-max", "--MaximumOutputTimestamp", type = int, help = "Maximum output timestamp time (in ns)", default = None)

# Parse args and execute given command
args = parser.parse_args()
args.func(args)

ConfigFile.close()
