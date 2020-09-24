

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;
	use work.JSON.all;
	

package Injector_PKG is

    -- Function declarations for organizing data from JSON config file
    function FillTargetMessageSizeArray(TargetPayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector;
    function FillSourceMessageSizeArray(SourcePayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector;
    function FindMaxPayloadSize(TargetPayloadSizeArray: integer_vector) return integer;
    function BuildHeaders(InjCFG: T_JSON; PlatCFG: T_JSON; HeaderSize: integer; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return HeaderFlits_t;
    function BuildPayloads(InjCFG: T_JSON; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return PayloadFlits_t;

end package Injector_PKG;


package body Injector_PKG is

    -- Fills array of source message size for each source PE
    function FillSourceMessageSizeArray(SourcePayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector is
        variable SourceMessageSizeArray : integer_vector(SourcePayloadSizeArray'range);
    begin

        FillSourceMessageSizeLoop: for i in SourcePayloadSizeArray'range loop 
            SourceMessageSizeArray(i) := SourcePayloadSizeArray(i) + HeaderSize;
        end loop FillSourceMessageSizeLoop;

        return SourceMessageSizeArray;

    end function;


    -- Fills array of target message size (Payload + Header) for each target PE
    function FillTargetMessageSizeArray(TargetPayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector is
        variable TargetMessageSizeArray: integer_vector(TargetPayloadSizeArray'range);
    begin

        FillTargetMessageSizeLoop : for i in TargetPayloadSizeArray'range loop
            TargetMessageSizeArray(i) := TargetPayloadSizeArray(i) + HeaderSize;
        end loop;
        
        return TargetMessageSizeArray;
        
    end function FillTargetMessageSizeArray;

    -- Builds header for each target PE
    function BuildHeaders(InjCFG: T_JSON; PlatCFG: T_JSON; HeaderSize: integer; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return HeaderFlits_t is
        
        variable Headers: HeaderFlits_t(TargetPEsArray'range, 0 to HeaderSize - 1);
        variable headerFlitString: string(1 to 4);
        
        variable timestampFlag: integer := jsonGetInteger(InjCFG, "timestampFlag");
        constant AmountOfPEs: integer := jsonGetInteger(PlatCFG, "AmountOfPEs");
        constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
        constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
        constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");
	    
	    variable myID: integer := jsonGetInteger(InjCFG, "PEPos");
        variable myWrapper:	integer := jsonGetInteger(PlatCFG, "WrapperAddresses/" & integer'image(myID));
        variable targetID: integer;
        variable targetWrapper: integer;

    begin

    	--report "Compiling header flits" severity note;

        BuildHeaderLoop: for target in TargetPEsArray'range loop
        
        	targetID := TargetPEsArray(target);
        	targetWrapper := WrapperAddresses(TargetID);
        	
        	--report "    Compiling header for target PE " & integer'image(targetID) severity note;

            BuildFlitLoop: for flit in 0 to (HeaderSize - 1) loop

                -- A header flit can be : "ADDR" (Address of target PE in network)
                --                        "SIZE" (Size of payload in this message)
                --                        "TIME" (Timestamp (in clock cycles) of when first flit of message leaves the injector)
                --                        "BLNK" (Fills with zeroes)
                
                headerFlitString := jsonGetString(InjCFG, ( "Headers/" & "Header" & integer'image(targetID) & "/" & integer'image(flit)));

                if headerFlitString = "ADDR" then 

                    -- Wrapper Address @ least significative bits (used for NoC routing)
                    Headers(target, flit)((DataWidth/2) - 1 downto 0) := RouterAddress(targetWrapper, NoCXSize);
                    
                    -- PE ID @ most significative bits (unique network address)
                    Headers(target, flit)(DataWidth - 1 downto DataWidth/2) := RouterAddress(targetID, SquareNoCBound);

                elsif headerFlitString = "SIZE" then

                    Headers(target, flit) := std_logic_vector(to_unsigned(TargetPayloadSizeArray(target), DataWidth));

                elsif headerFlitString = "TIME" then

                    Headers(target, flit) := std_logic_vector(to_unsigned(timestampFlag, DataWidth));

                elsif headerFlitString = "BLNK" then

                    Headers(target, flit) := (others => '0');

                else

                     --report "        Flit " & integer'image(flit) & " of header of message to be delivered to PE ID " & integer'image(TargetPEsArray(target)) & " is not defined" severity warning;

                end if;

                --report "        Flit " & integer'image(flit) & " of header of message to be delivered to PE ID " & integer'image(TargetPEsArray(target)) & " is " & headerFlitString & " = " & integer'image(to_integer(unsigned(Headers(target, flit)))) severity note;

            end loop BuildFlitLoop;

        end loop BuildHeaderLoop;

        return Headers;

    end function BuildHeaders;


    -- Builds payload for each target PE
    function BuildPayloads(InjCFG: T_JSON; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return PayloadFlits_t is

        variable MaxPayloadSize : integer := FindMaxPayloadSize(TargetPayloadSizeArray);
        variable Payloads : PayloadFlits_t(TargetPEsArray'range, 0 to MaxPayloadSize - 1);
        variable payloadFlitString : string(1 to 5);
        variable timestampFlag : integer := jsonGetInteger(InjCFG, "timestampFlag");
        variable amountOfMessagesSentFlag : integer := jsonGetInteger(InjCFG, "amountOfMessagesSentFlag");

        -- RNG
        variable RNGSeed1: integer := 22;
        variable RNGSeed2: integer := 32;
        variable RandomNumber: real;

    begin

    	report "Compiling payload flits" severity note;

        BuildPayloadLoop: for target in TargetPayloadSizeArray'range loop

        	report "    Compiling payload for target PE " & integer'image(TargetPEsArray(target)) severity note;

            BuildFlitLoop: for flit in 0 to (MaxPayloadSize - 1) loop 


                -- Checks if current target has had its payload fully compiled (if the inner loop iterator > PayloadSize(target), break inner loop)
                if flit = TargetPayloadSizeArray(target) then
                    exit;
                end if;

                --                                                                                Translates loop iterator to PE ID
                payloadFlitString := jsonGetString(InjCFG, "Payloads/" & "Payload" & integer'image(TargetPEsArray(target)) & "/" & integer'image(flit) );

                -- A payload flit can be : "PEPOS" (PE position in network), 
                --                         "APPID" (ID of app being emulated by this injector), 
                --                         "THDID" (ID of thread of the app being emulated in this PE),
                --                         "AVGPT" (Average processing time of a message received by the app being emulated by this PE),
                --                         "TMSTP" (Timestamp of message being sent (to be set in real time, not in this function)),
                --                         "AMMSG" (Amount of messages sent by this PE (also to be se in real time)),
                --                         "RANDO" (Randomize every bit)
                --                         "BLANK" (Fills with zeroes)
                
                if payloadFlitString = "PEPOS" then

                    Payloads(target, flit) := std_logic_vector(to_unsigned(jsonGetInteger(InjCFG, "PEPos"), DataWidth));

                elsif payloadFlitString = "APPID" then

                    Payloads(target, flit) := std_logic_vector(to_unsigned(jsonGetInteger(InjCFG, "APPID"), DataWidth));

                elsif payloadFlitString = "THDID" then

                    Payloads(target, flit) := std_logic_vector(to_unsigned(jsonGetInteger(InjCFG, "ThreadID"), DataWidth));

                elsif payloadFlitString = "AVGPT" then

                    --Payloads(target, flit) := std_logic_vector(to_unsigned(jsonGetInteger(InjectorJSONConfig, "AverageProcessingTimeInClockPulses"), DataWidth));
                    Payloads(target, flit) := (others => '1');

                elsif payloadFlitString = "TMSTP" then

                    -- Flags for "real time" processing
                    Payloads(target, flit) := std_logic_vector(to_unsigned(timestampFlag, DataWidth));

                elsif payloadFlitString = "AMMSG" then 

                    -- Flags for "real time" processing
                    Payloads(target, flit) := std_logic_vector(to_unsigned(amountOfMessagesSentFlag, DataWidth));

                elsif payloadFlitString = "RANDO" then

                    -- Randomizes each bit of current flit
                    for i in 0 to DataWidth - 1 loop

                        -- RandomNumber <= (0.0 < RNG < 1.0)
                        Uniform(RNGSeed1, RNGSeed2, RandomNumber);

                        if RandomNumber < 0.5 then

                            Payloads(target, flit)(i) := '0';

                        else

                            Payloads(target, flit)(i) := '1';

                        end if;

                    end loop;

                elsif payloadFlitString = "BLANK" then

                    Payloads(target, flit) := (others=>'0');

                end if;

                report "        Flit " & integer'image(flit) & " of payload of message to be delivered to PE ID " & integer'image(TargetPEsArray(target)) & " is " & payloadFlitString & " = " & integer'image(to_integer(unsigned(Payloads(target, flit)))) severity note;

            end loop BuildFlitLoop;

        end loop BuildPayloadLoop;

        return Payloads;

    end function BuildPayloads;


    -- Returns highest value in the TargetPayloadSizeArray array
    function FindMaxPayloadSize(TargetPayloadSizeArray: integer_vector) return integer is
        variable MaxPayloadSize : integer := 0;
    begin

        FindMaxPayloadSizeLoop : for i in TargetPayloadSizeArray'range loop
            
            if TargetPayloadSizeArray(i) > MaxPayloadSize then

                MaxPayloadSize := TargetPayloadSizeArray(i);

            end if;

        end loop FindMaxPayloadSizeLoop;

        return MaxPayloadSize;

    end function FindMaxPayloadSize;


end package body Injector_PKG;