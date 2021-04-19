--------------------------------------------------------------------------------
-- Title       : Injector
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : Injector.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Parametric NoC packet injector
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : Implement real time randomization of flits
--               Only check Enable when flitCounter = 0
--------------------------------------------------------------------------------

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.math_real.trunc; -- for random number generation
    use ieee.std_logic_unsigned.all;
    use ieee.numeric_std.all;

library std;
    use std.textio.all;

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;
    use HyHeMPS.Injector_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;
    --use work.Injector_PKG.all;
    --use work.JSON.all;


entity Injector is

	generic(
        InjectorConfigFile: string;
        PlatformConfigFile: string;
        OutboundLogFilename: string
	);

	port(

		-- Basic
		Clock: in std_logic;
		Reset: in std_logic;

        -- Input Interface (From Trigger)
        Enable: in std_logic;

        -- Output Interface (To Trigger)
        LastFlitFlag: out std_logic;

		-- Output Interface (To Output Buffer)
		DataOut: out DataWidth_t;
		DataOutAV: out std_logic;
        OutputBufferAvailableFlag: in std_logic

	);

end entity Injector;


architecture RTL of Injector is

    -- JSON configuration files
    constant InjectorJSONConfig: T_JSON := jsonLoad(InjectorConfigFile);
    constant PlatformJSONConfig: T_JSON := jsonLoad(PlatformConfigFile);

    -- Message Flow type (Only "CBR" currently supported)
    constant FlowType: string(1 to 3) := jsonGetString(InjectorJSONConfig, "FlowType");

    -- Emulated Workload Values
    constant Bandwidth: integer := jsonGetInteger(InjectorJSONConfig, "Bandwidth");  -- in MBps
    constant SourcePEPos: integer := jsonGetInteger(InjectorJSONConfig, "SourcePEPos");
    constant SourceBaseNoCPos: integer := jsonGetInteger(InjectorJSONConfig, "SourceBaseNoCPos");
    constant SourceThreadID: integer := jsonGetInteger(InjectorJSONConfig, "SourceThreadID");
    constant SourceThreadName: string := jsonGetString(InjectorJSONConfig, "SourceThreadName");
    constant TargetPEPos: integer := jsonGetInteger(InjectorJSONConfig, "TargetPEPos");
    constant TargetBaseNoCPos: integer := jsonGetInteger(InjectorJSONConfig, "TargetBaseNoCPos");
    constant TargetThreadID: integer := jsonGetInteger(InjectorJSONConfig, "TargetThreadID");
    constant TargetThreadName: string := jsonGetString(InjectorJSONConfig, "TargetThreadName");
    constant AppID: integer := jsonGetInteger(InjectorJSONConfig, "AppID");
    constant AppName: string := jsonGetString(InjectorJSONConfig, "AppName");
    constant WorkloadName: string := jsonGetString(InjectorJSONConfig, "WorkloadName");
    
    -- Message Header
    constant HeaderSize: integer := jsonGetInteger(InjectorJSONConfig, "HeaderSize");
    constant HeaderFlits: DataWidth_vector(0 to HeaderSize - 1) := BuildHeader(InjectorJSONConfig, PlatformJSONConfig);

    -- Message Payload
    constant PayloadSize: integer := jsonGetInteger(InjectorJSONConfig, "PayloadSize");
    constant PayloadFlits: DataWidth_vector(0 to PayloadSize - 1) := BuildPayload(InjectorJSONConfig);

    -- Compiled Message (Header + Payload)
    constant MessageSize : integer := HeaderSize + PayloadSize; 
    constant MessageFlits: DataWidth_vector(0 to MessageSize - 1) := HeaderFlits & PayloadFlits;

    -- Payload Real Time 
    constant AmountOfMessagesSentFlag: integer := jsonGetInteger(InjectorJSONConfig, "AmountOfMessagesSentFlag");
    --constant RealTimeRandomFlag: integer := jsonGetInteger(InjectorJSONConfig, "RealTimeRandomFlag");
    constant TimestampFlag: integer := jsonGetInteger(InjectorJSONConfig, "TimestampFlag");

    -- RNG seeds (for real time randomization of flits, currently not implemented)
    --signal RNGSeed1: integer := jsonGetInteger(InjectorJSONConfig, "RNGSeed1");
    --signal RNGSeed2: integer := jsonGetInteger(InjectorJSONConfig, "RNGSeed2");

    -- Opens log file
    file OutboundLog: text open write_mode is OutboundLogFilename;

begin

    process(Clock, Reset) 

        variable currentFlit: DataWidth_t := (others => '0');
        variable flitCounter: integer := 0;

        variable firstFlitOutTimestamp: DataWidth_t := (others=>'0');
        variable amountOfMessagesSent: DataWidth_t := (others=>'0');

        variable OutboundLogLine: line;

    begin

        if Reset = '1' then

            DataOut <= (others => '0');
            DataOutAV <= '0';
            LastFlitFlag <= '0';

            currentFlit := (others => '0');
            flitCounter := 0;

            firstFlitOutTimestamp := (others => '0');
            amountOfMessagesSent := (others => '0');

        elsif rising_edge(Clock) then

            if (flitCounter = 0 and Enable = '1') or flitCounter > 0 then

                if OutputBufferAvailableFlag = '1' then

                    -- Updates real time values and log
                    if flitCounter = 0 then

                        firstFlitOutTimestamp := std_logic_vector(to_unsigned((now / 1 ns), DataWidth));
                        amountOfMessagesSent := amountOfMessagesSent + 1;

                        -- Write to log file ( | target ID | source ID | payload size | timestamp | )
                        write(OutboundLogLine, integer'image(TargetPEPos) & " ");
                        write(OutboundLogLine, integer'image(SourcePEPos) & " ");
                        write(OutboundLogLine, integer'image(PayloadSize) & " ");
                        write(OutboundLogLine, integer'image(now / 1 ns));
                        writeline(OutboundLog, OutboundLogLine);

                    end if;

                    -- Determines current flit
                    currentFlit := MessageFlits(flitCounter);

                    -- Replaces real time flags with actual values
                    if currentFlit = TimestampFlag then
                        currentFlit := firstFlitOutTimestamp;

                    elsif currentFlit = AmountOfMessagesSentFlag then
                        currentFlit := amountOfMessagesSent;

                    end if;

                    -- Places flit on output interface
                    DataOut <= currentFlit;
                    DataOutAV <= '1';

                    -- Sets LastFlitFlag
                    if flitCounter = MessageSize - 1 then
                        LastFlitFlag <= '1';
                    else
                        LastFlitFlag <= '0';
                    end if;

                    -- Updates counter
                    flitCounter := incr(flitCounter, MessageSize - 1, 0);

                else

                    report "No available slot on output buffer at PEPos <" & integer'image(SourcePEPos) & ">" severity warning;

                end if;

            else

                DataOutAV <= '0';    
                    
            end if;

        end if;

    end process;

    -- Certifies FlowType is "CBR" 
    --assert FlowType = "CBR" report "Error: FlowType <" & FlowType & "> is not recognized, only \"CBR\" FlowType is currently supported" severity <ERROR>;

end architecture RTL;
