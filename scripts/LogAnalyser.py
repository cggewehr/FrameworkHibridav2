
class Message:

    # Constructor
    def __init__(self, InputString):

        # An Input log line should look like: ( | target ID | source ID | msg size | output timestamp | input timestamp | )
        # An Output log line should look like: ( | target ID | source ID | msg size | output timestamp | )
        logEntry = InputString.split()  # split() method takes a string of whitespace separated values and outputs a list of those same values
        self.TargetID = int(logEntry[0])
        self.SourceID = int(logEntry[1])
        self.MessageSize = int(logEntry[2])
        self.OutputTimestamp = int(logEntry[3])

        # If log has a 5th entry (Input Timestamp field), its an input log entry
        try:
            self.InputTimestamp = int(logEntry[4])
            #self.isInputEntry = True
        except IndexError:
            #self.isInputEntry = False
            pass

    # Overloads operator " = " (Compares 2 Message objects, used for comparing an input entry to an output entry)
    def __eq__(self, comp):
        if (self.TargetID == comp.TargetID and self.SourceID == comp.SourceID
                and self.MessageSize == comp.MessageSize and self.OutputTimestamp == comp.OutputTimestamp):
            return True
        else:
            return False

    def __str__(self):
        try:
            return ("\nTargetID = " + str(self.TargetID) +
                    "\nSourceID = " + str(self.SourceID) +
                    "\nMessageSize = " + str(self.MessageSize) +
                    "\nOutputTimestamp = " + str(self.OutputTimestamp) +
                    "\nInputTimestamp = " + str(self.InputTimestamp))

        except AttributeError:  # No InputTimestamp attribute
            return ("\nTargetID = " + str(self.TargetID) +
                    "\nSourceID = " + str(self.SourceID) +
                    "\nMessageSize = " + str(self.MessageSize) +
                    "\nOutputTimestamp = " + str(self.OutputTimestamp))


class Log:

    # Constructor
    def __init__(self, logType):
        self.Entries = []
        self.logType = logType

    # Adds a Message object to Entries array
    def addEntry(self, Message):
        self.Entries.append(Message)

    def __str__(self):
        tempString = ""

        tempString += ("\tLogtype = " + str(self.logType) + "\n")

        for i, Entry in enumerate(self.Entries):
            tempString += ("\n\tEntry " + str(i))
            tempString += str(Entry)
            tempString += "\n"

        return tempString


#                                                     Entry Point
########################################################################################################################


# Expects as arguments: $1 = Project directory ; $2 = Debug flag
def loganalyser(argv):

    import os
    import sys

    # Sets argument values
    try:
        #ProjectDir = str(sys.argv[1])
        ProjectDir = argv[0]
    except IndexError:
        ProjectDir = ""

    try:
        #debugFlag = int(sys.argv[2])
        debugFlag = argv[1]
    except IndexError:
        debugFlag = 0

    # Sets up proper cwd (directory in which log .txt's are contained)
    CurrentDir = os.path.basename(os.path.normpath(os.getcwd()))

    if CurrentDir == "log":
        pass

    elif CurrentDir == ProjectDir:
        os.chdir(os.getcwd() + "/log")
        
    else:
    
        if ProjectDir == "":
            print("Error: Please give a project directory as argv[1] if not executing this script directly at a ~/log directory")
            exit(1)

        try:
            os.chdir(os.getcwd() + ProjectDir + "/log")

        except OSError:
            print("Error: Given directory \"" + ProjectDir + "\" not found at path " + os.getcwd())
            exit(1)
            
    # Starts script execution
    print("Looking for log files at " + os.getcwd())

    # Inits aux variables
    InLogs = dict()
    OutLogs = dict()

    # Builds Log objects from text files. Loop through every file in cwd
    for File in os.listdir(os.getcwd()):

        if File.startswith("InLog") and File.endswith(".txt"):
            currentLog = Log("Input")  # Current file is an input log
            LogNumber = int(File[File.index("InLog")+len("InLog"):File.index(".txt")])

        elif File.startswith("OutLog") and File.endswith(".txt"):
            currentLog = Log("Output")  # Current file is an output log
            LogNumber = int(File[File.index("OutLog")+len("OutLog"):File.index(".txt")])

        else:
            continue  # Current file is neither an input nor output log

        # Since current file is a log, open it
        LogFile = open(File, "r")

        # Loop through every line in LogFile and add it as a Message object to Log object 
        for Line in LogFile.readlines():
            currentLog.addEntry(Message(Line))

        # Append Log object to InLogs or OutLogs lists, depending on its type
        if currentLog.logType == "Input":
            InLogs[LogNumber] = currentLog

        else:
            OutLogs[LogNumber] = currentLog

    print("Found " + str(len(InLogs)) + " input logs")
    print("Found " + str(len(OutLogs)) + " output logs")

    # Inits computation variables
    amountOfPEs = len(InLogs)  
    avgLatencies = [[0 for i in range(amountOfPEs)] for j in range(amountOfPEs)]
    avgLatenciesCounters = [[0 for i in range(amountOfPEs)] for j in range(amountOfPEs)]
    missCount = [[0 for i in range(amountOfPEs)] for j in range(amountOfPEs)]
    hitCount = [[0 for i in range(amountOfPEs)] for j in range(amountOfPEs)]      

    # Prints out Log objects if debug flag is active
    if debugFlag != 0:
        for InLog in InLogs:
            print("\t\tIn log " + str(i) + "\n")
            print(InLog)
        for OutLog in OutLogs:
            print("\t\tOut log " + str(i) + "\n")
            print(OutLog)

    # Tries to find an In log entry match for every Out log entry
    for currentOutLog in OutLogs:

        currentOutLog = OutLogs[currentOutLog]

        # Loop through all entries in current Out log
        for currentOutEntry in currentOutLog.Entries:

            #currentOutEntry = currentOutLog.Entries[j]
            currentTarget = currentOutEntry.TargetID
            currentInLog = InLogs[currentTarget]
            foundFlag = False

            # Loop through all entries of current In log, compares each of them to current message in current Out log
            for currentInEntry in currentInLog.Entries:

                #currentInEntry = currentInLog.Entries[k]

                if currentOutEntry == currentInEntry:

                    # Found match for current message
                    currentLatency = currentInEntry.InputTimestamp - currentOutEntry.OutputTimestamp

                    if debugFlag == 1:
                        print("Found match for message " + str(j) + " sent by ID = " +
                            str(currentOutEntry.SourceID) + " to target " + str(currentOutEntry.TargetID) +
                            " with size " + str(currentOutEntry.MessageSize) + " with latency = " + str(currentLatency))
                    foundFlag = True

                    # Update average latency value (https://blog.demofox.org/2016/08/23/incremental-averaging/)
                    src = currentOutEntry.SourceID
                    tgt = currentOutEntry.TargetID
                    avgLatenciesCounters[src][tgt] += 1
                    avgLatencies[src][tgt] += (currentLatency - avgLatencies[src][tgt]) / avgLatenciesCounters[src][tgt]
                    hitCount[src][tgt] += 1

                    break

            if not foundFlag:
                missCount[currentOutEntry.SourceID][currentOutEntry.TargetID] += 1

                if debugFlag == 1:
                    print("No match found for message" + str(j) + " sent by ID = " + str(currentOutEntry.SourceID) +
                          " to target " + str(currentOutEntry.TargetID) + " with size " + str(currentOutEntry.MessageSize))

    # Prints out amount of successfully delivered messages
    print("\n\tSuccessfully Delivered Messages")
    for target in range(amountOfPEs):
        for source in range(amountOfPEs):
            if hitCount[source][target] + missCount[source][target] > 0:
                print("Messages successfully delivered from PE ID " + str(source) + " to PE ID " + str(target) + ": " +
                      str(hitCount[source][target]) + "/" + str(hitCount[source][target] + missCount[source][target]))

    # Prints out average latency values
    print("\n\tAverage Latency Values:")
    for target in range(amountOfPEs):
        for source in range(amountOfPEs):
            if avgLatencies[source][target] != 0:
                print("Average latency from PE ID " + str(source) + " to PE ID " + str(target) + " = " + str(
                      avgLatencies[source][target]) + " ns")


    print("")
