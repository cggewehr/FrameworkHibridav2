---------------------------------------------------------------------------------------------------------
-- DESIGN UNIT  : MSG Injector (Fixed injection rate or dependent)                                     --
-- DESCRIPTION  :                                                                                      --
-- AUTHOR       : Carlos Gabriel de Araujo Gewehr                                                      --
-- CREATED      : Aug 13th, 2019                                                                       --
-- VERSION      : v0.1                                                                                 --
-- HISTORY      : Version 0.1 - Aug 13th, 2019                                                         --
---------------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------------
-- TODO         : 
    -- Make more JSON test cases
    -- Support task migration emulation
    -- Generalize message bursts to any number of targets
---------------------------------------------------------------------------------------------------------

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.math_real.trunc; -- for random number generation
    use ieee.std_logic_unsigned.all;
    use ieee.numeric_std.all;

library std;
    use std.textio.all;

library work;
    use work.HyHeMPS_PKG.all;
    use work.JSON.all;

entity Injector is

	generic (
        PEConfigFile          : string := "PESample.json";
        InjectorConfigFile    : string := "InjectorSample.json";
        PlatformConfigFile    : string := "PlatformSample.json"; 
        OutboundLogFilename   : string := "OutLogTest.txt"
	);

	port (

		-- Basic
		Clock : in std_logic;
		Reset : in std_logic;

		-- Output Interface
		DataOut : out DataWidth_t;
		DataOutAV : out std_logic;
        OutputBufferSlotAvailable : in std_logic

	);

end entity Injector;

architecture RTL of Injector is

    -- JSON configuration file
    constant InjectorJSONConfig: T_JSON := jsonLoad(InjectorConfigFile);
    constant PEJSONConfig: T_JSON := jsonLoad(PEConfigFile);
    constant PlatformJSONConfig: T_JSON := jsonLoad(PlatformConfigFile);

    -- Injector type ("FXD" or "DPD")
    constant InjectorType: string(1 to 3) := jsonGetString(InjectorJSONConfig, "InjectorType");

    -- Message Flow type ("RND" or "DTM")
    constant FlowType: string(1 to 3) := jsonGetString(InjectorJSONConfig, "FlowType");

    -- Fixed injection rate injector constants
    constant InjectionRate: integer range 0 to 100 := jsonGetInteger(InjectorJSONConfig, "InjectionRate");

    -- Dependant injector constants
    constant PEPos: integer := jsonGetInteger(PEJSONConfig, "PEPos");
    constant AppID: integer := jsonGetInteger(PEJSONConfig, "AppID");
    constant ThreadID: integer := jsonGetInteger(PEJSONConfig, "ThreadID");
    constant AverageProcessingTimeInClockPulses: integer := jsonGetInteger(PEJSONConfig, "AverageProcessingTimeInClockPulses");

    -- Source PEs constants
    --constant AmountOfSourcePEs: integer := jsonGetInteger(InjectorJSONConfig, "AmountOfSourcePEs");
    --constant SourcePEsArray: SourcePEsArray_t(0 to AmountOfSourcePEs - 1) := FillSourcePEsArray(InjectorJSONConfig, AmountOfSourcePEs);
    --constant SourcePEsArray: integer_vector(0 to AmountOfSourcePEs - 1) := jsonGetIntegerArray(InjectorJSONConfig, "SourcePEs");

    -- Target PEs constants (Lower numbered targets in JSON have higher priority (target number 0 will have the highest priority)
    constant AmountOfTargetPEs: integer := jsonGetInteger(InjectorJSONConfig, "AmountOfTargetPEs");
    constant TargetPEsArray: integer_vector(0 to AmountOfTargetPEs - 1) := jsonGetIntegerArray(InjectorJSONConfig, "TargetPEs");
    --constant AmountOfMessagesInBurstArray: AmountOfMessagesInBurstArray_t(0 to AmountOfTargetPEs - 1) := FillAmountOfMessagesInBurstArray(InjectorJSONConfig, AmountOfTargetPEs);
    constant AmountOfMessagesInBurstArray: integer_vector(0 to AmountOfTargetPEs - 1) := jsonGetIntegerArray(InjectorJSONConfig, "AmountOfMessagesInBurst");
    --constant WrapperAddressTableArray: WrapperAddressTableArray_t(0 to AmountOfTargetPEs - 1) := FillWrapperAddressTableArray(PlatformJSONConfig, TargetPEsArray);

    -- Message parameters 
    --constant TargetPayloadSizeArray: TargetPayloadSizeArray_t(0 to AmountOfTargetPEs - 1) := FillTargetPayloadSizeArray(InjectorJSONConfig, AmountOfTargetPEs);
    constant TargetPayloadSizeArray: integer_vector(0 to AmountOfTargetPEs - 1) := jsonGetIntegerArray(InjectorJSONConfig, "TargetPayloadSize");
    --constant SourcePayloadSizeArray: SourcePayloadSizeArray_t(0 to AmountOfSourcePEs - 1) := FillSourcePayloadSizeArray(InjectorJSONConfig, AmountOfSourcePEs);
    --constant SourcePayloadSizeArray: integer_vector(0 to AmountOfSourcePEs - 1) := jsonGetIntegerArray(InjectorJSONConfig, "SourcePayloadSize");
    constant MaxPayloadSize: integer := FindMaxPayloadSize(TargetPayloadSizeArray);

    constant HeaderSize: integer := jsonGetInteger(InjectorJSONConfig, "HeaderSize");
    constant HeaderFlits: HeaderFlits_t(0 to AmountOfTargetPEs - 1, 0 to HeaderSize - 1) := BuildHeaders(InjectorJSONConfig, PlatformJSONConfig, HeaderSize, TargetPayloadSizeArray, TargetPEsArray);

    --constant TargetMessageSizeArray: TargetMessageSizeArray_t(0 to AmountOfTargetPEs - 1) := FillTargetMessageSizeArray(TargetPayloadSizeArray, HeaderSize); 
    constant TargetMessageSizeArray: integer_vector(0 to AmountOfTargetPEs - 1) := FillTargetMessageSizeArray(TargetPayloadSizeArray, HeaderSize); 
    --constant SourceMessageSizeArray : SourceMessageSizeArray_t := FillSourceMessageSizeArray(SourcePayloadSizeArray, HeaderSize);
    --constant SourceMessageSizeArray : integer_vector := FillSourceMessageSizeArray(SourcePayloadSizeArray, HeaderSize);

    constant PayloadFlits: PayloadFlits_t(TargetPayloadSizeArray'range, 0 to MaxPayloadSize - 1) := BuildPayloads(InjectorJSONConfig, TargetPayloadSizeArray, TargetPEsArray);

    -- Payload Flags
    constant timestampFlag: integer := jsonGetInteger(InjectorJSONConfig, "timestampFlag");
    constant amountOfMessagesSentFlag: integer := jsonGetInteger(InjectorJSONConfig, "amountOfMessagesSentFlag");

    -- Semaphore for flow control if DPD injector is instantiated
    --signal semaphore: integer range 0 to UINT32MaxValue := 0;

begin

    -- Generates fixed rate injector (injects flit at a fixed rate)
    FixedRateInjector: if (InjectorType = "FXD" and InjectionRate /= 0) generate

        -- Generates messages at a specific rate. (Only instanciated if InjectorType is set as "FXD" on JSON config file).
        FXD: block is

            type state_t is (Sreset, Swaiting, Ssending);
            signal currentState: state_t;

            signal currentTargetPE: integer := 0;
            signal injectionCounter: integer := 0;
            signal injectionPeriod: integer := ((TargetMessageSizeArray(0) * 100) / InjectionRate) - TargetMessageSizeArray(0);
            signal burstCounter: integer := 0;

            file OutboundLog: text open write_mode is OutboundLogFilename;

        begin

            -- Sends out messages at a constant injection rate. (Only instanciated if InjectorType is set as "FXD" on JSON config file).
            FixedRateInjetorProcess: process(Clock)

                variable flitTemp: DataWidth_t := (others=>'0');
                variable firstFlitOutTimestamp: DataWidth_t := (others=>'0');
                variable amountOfMessagesSent: DataWidth_t := (others=>'0');

                -- RNG (Used by the Uniform function)
                variable RNGSeed1 : integer := jsonGetInteger(InjectorJSONConfig, "RNGSeed1");
                variable RNGSeed2 : integer := jsonGetInteger(InjectorJSONConfig, "RNGSeed2");
                variable randomNumber : real;

                variable OutboundLogLine: line;

            begin

                if rising_edge(Clock) then

                    if Reset = '1' then

                        currentState <= Sreset;

                    else

                        if currentState = Sreset then

                            injectionCounter <= 0;
                            injectionPeriod <= ( (TargetMessageSizeArray(0) * 100) / InjectionRate) - TargetMessageSizeArray(0);

                            --OutputBufferWriteRequest <= '0';
                            DataOutAV <= '0';

                            firstFlitOutTimestamp := (others=>'0');
                            amountOfMessagesSent := (others=>'0');

                            currentTargetPE <= 0;
                            burstCounter <= 0;

                            -- Generates a new random number
                            Uniform(RNGSeed1, RNGSeed2, RandomNumber);

                            currentState <= Ssending;

                        -- Sends a flit to output buffer
                        elsif currentState = Ssending then

                            -- Sends a flit to buffer
                            if OutputBufferSlotAvailable = '1' then

                                -- If this is the first flit in the message, saves current ClkCounter (to be sent as a flit when a payload flit is equal to the timestampFlag)
                                if injectionCounter = 0 then

                                    --firstFlitOutTimestamp := std_logic_vector(to_unsigned(clockCounter, DataWidth));
                                    firstFlitOutTimestamp := std_logic_vector(to_unsigned((now / 1 ns), DataWidth));

                                    -- Write to log file ( | target ID | source ID | payload size | timestamp | )
                                    write(OutboundLogLine, integer'image(TargetPEsArray(currentTargetPE)) & " ");
                                    write(OutboundLogLine, integer'image(PEPos) & " ");
                                    write(OutboundLogLine, integer'image(TargetPayloadSizeArray(currentTargetPE)) & " ");
                                    --write(OutboundLogLine, integer'image(clockCounter));
                                    write(OutboundLogLine, integer'image(now / 1 ns));
                                    writeline(OutboundLog, OutboundLogLine);

                                    amountOfMessagesSent := amountOfMessagesSent + 1;

                                end if;

                                -- Decides what flit to send (Header or Payload)
                                if injectionCounter < HeaderSize then

                                    -- A Header flit will be sent
                                    flitTemp := HeaderFlits(currentTargetPE, injectionCounter);

                                -- Not a header flit
                                else

                                    -- A Payload flit will be sent
                                    flitTemp := PayloadFlits(currentTargetPE, injectionCounter - HeaderSize);

                                end if;

                                -- Replaces real time flags with respective value
                                if flitTemp = timestampFlag then

                                    flitTemp := firstFlitOutTimestamp;

                                elsif flitTemp = amountOfMessagesSentFlag then

                                    flitTemp := amountOfMessagesSent;

                                end if;

                                -- Outbound data bus receives the flit to be sent
                                DataOut <= flitTemp;
                                DataOutAV <= '1';
                                --OutputBufferWriteRequest <= '1';

                                -- Increments flits sent counter
                                injectionCounter <= injectionCounter + 1;
                                
                                -- Decides whether to send another flit or idle to maintain injection rate (Checks if message has ended)
                                if (injectionCounter + 1) = TargetMessageSizeArray(currentTargetPE) then

                                    -- Message has been sent
                                    injectionCounter <= 0;
                                    burstCounter <= burstCounter + 1;

                                    -- If injection rate = 100%, dont idle next state, else, do idle to maintain injection rate
                                    if InjectionRate = 100 then
                                    	currentState <= Ssending;
                                    else
                                    	currentState <= Swaiting;
                                    end if; 
    
                                    -- Determines if burst has ended
                                    if (burstCounter + 1) = AmountOfMessagesInBurstArray(currentTargetPE) then

                                        burstCounter <= 0;

                                        -- Determines next target PE
                                        if FlowType = "RND" then

                                            -- Uses Uniform procedure from ieee.math_real. currentTargetPE gets a value between 0 and (AmountOfTargetPEs - 1)
                                            currentTargetPE <= integer(RandomNumber * real(AmountOfTargetPEs - 1));

                                            -- Generates a new random number
                                            Uniform(RNGSeed1, RNGSeed2, RandomNumber);

                                        elsif FlowType = "DTM" then

                                            -- Next message will be sent to next sequential target as defined on TargetPEsArray
                                            currentTargetPE <= incr(currentTargetPE, AmountOfTargetPEs - 1, 0);

                                        end if;

                                    end if;

                                else

                                    -- Message has not ended, will send another flit next state
                                    currentState <= Ssending;

                                end if;

                            else  -- outputBufferSlotAvailable = '0' (Cant write to buffer)

                                report "No available slot on output buffer at network address: " & integer'image(PEPOS) severity warning;
                                currentState <= Ssending;

                            end if;
                            
                         -- Idles to maintain defined injection rate
                        elsif currentState = Swaiting then

                            -- Signals DataOut isn't valid
                            DataOutAV <= '0';
                            --OutputBufferWriteRequest <= '0';

                            -- Increments flit counter
                            injectionCounter <= injectionCounter + 1;

                            -- Decides whether to send another flit or idle to maintain injection rate
                            if injectionCounter = injectionPeriod + 1 then

                                injectionCounter <= 0;
                                currentState <= Ssending;

                                -- Gets new injection period value (according to new message)
                                injectionPeriod <= ( (TargetMessageSizeArray(currentTargetPE) * 100) / InjectionRate) - TargetMessageSizeArray(currentTargetPE);

                            else

                                currentState <= Swaiting;
                                
                            end if;

                        end if;

                    end if;

                end if;

            end process;

        end block FXD;

    end generate FixedRateInjector;


end architecture RTL;
