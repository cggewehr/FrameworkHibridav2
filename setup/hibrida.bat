set HIBRIDA_NAME=hibrida
set HIBRIDA_PATH=D:\GitKraken\FrameworkHibridav2
set PATH=%PATH%;%HIBRIDA_PATH%/scripts
doskey hibrida=(python D:\GitKraken\FrameworkHibridav2\scripts\mainScript.py $*)
set HIBRIDA_DEFAULT_DIRECTORY=C:\Users\c_ara/Desktop/HibridaProjects
set HIBRIDA_HARDWARE_PATH=%HIBRIDA_PATH%/src/hardware
set HIBRIDA_SOFTWARE_PATH=%HIBRIDA_PATH%/src/software
set HIBRIDA_APPCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/AppComposer
set HIBRIDA_PLATFORMCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/PlatformComposer
set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_APPCOMPOSER_PATH%
set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PLATFORMCOMPOSER_PATH%
set FLOWGEN_TOPOLOGIES_PATH=%HIBRIDA_PATH%/flowgenData/Topologies
set FLOWGEN_APPLICATIONS_PATH=%HIBRIDA_PATH%/flowgenData/Applications
set FLOWGEN_WORKLOADS_PATH=%HIBRIDA_PATH%/flowgenData/Workloads
set FLOWGEN_ALLOCATIONMAPS_PATH=%HIBRIDA_PATH%/flowgenData/AllocationMaps
set FLOWGEN_CLUSTERCLOCKS_PATH=%HIBRIDA_PATH%/flowgenData/ClusterClocks
