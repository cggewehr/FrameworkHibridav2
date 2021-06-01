--------------------------------------------------------------------------------
-- Title       : Injector_PKG
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : HyHeMPS_PKG.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Injector message compiling functions
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : Check if randomly generated flits are conflicting with real time flags
--               Add more possibilities to payload flits, such as Flow bandwidth, real time RNG, etc...
--------------------------------------------------------------------------------

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;
	--use work.JSON.all;
	

package Injector_PKG is

	type InjectorInterface is record

		Clock: std_logic;
		--Reset: std_logic;

		Enable: std_logic;
		LastFlitFlag: std_logic;

		DataOut : DataWidth_t;
		DataOutAV : std_logic;
        OutputBufferAvailableFlag : std_logic;

	end record;

	type InjectorInterface_vector is array(natural range <>) of InjectorInterface;

    -- Function declarations for organizing data from JSON config file
    function BuildHeader(InjCFG: T_JSON; PlatCFG: T_JSON) return DataWidth_vector;
    function BuildPayload(InjCFG: T_JSON) return DataWidth_vector;

end package Injector_PKG;


package body Injector_PKG is

    -- Builds header for each target PE
    function BuildHeader(InjCFG: T_JSON; PlatCFG: T_JSON) return DataWidth_vector is

        constant SourcePEPos: integer := jsonGetInteger(InjCFG, "SourcePEPos");
	    constant SourceBaseNoCPos: integer := jsonGetInteger(InjCFG, "SourceBaseNoCPos");
	    constant TargetPEPos: integer := jsonGetInteger(InjCFG, "TargetPEPos");
	    constant TargetBaseNoCPos: integer := jsonGetInteger(InjCFG, "TargetBaseNoCPos");

	    constant PayloadSize: integer := jsonGetInteger(InjCFG, "PayloadSize");
        
        variable TimestampFlag: integer := jsonGetInteger(InjCFG, "TimestampFlag");

        constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
        constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");

        constant HeaderSize: integer := jsonGetInteger(InjCFG, "HeaderSize");
        variable HeaderFlits: DataWidth_vector(0 to HeaderSize - 1);
        variable HeaderFlitString: string(1 to 4);

    begin

    	report "Compiling header for message from PE ID <" & integer'image(SourcePEPos) & "> to PE ID <" & integer'image(TargetPEPos) & ">" severity note;

        BuildFlitLoop: for flit in HeaderFlits'range loop

            -- A header flit can be : "ADDR" (Address of target PE in network)
            --                        "SIZE" (Size of payload in this message)
            --                        "TIME" (Timestamp (in nanoseconds) of when first flit of message leaves the injector)
            --                        "BLNK" (Fills with zeroes)
            
            HeaderFlitString := jsonGetString(InjCFG, ("Header/" & integer'image(flit)));

            if HeaderFlitString = "ADDR" then 

                -- Wrapper Address @ least significative bits (used for NoC routing)
                HeaderFlits(flit)((DataWidth/2) - 1 downto 0) := RouterAddress(TargetBaseNoCPos, NoCXSize);
                
                -- PE ID @ most significative bits (unique network address)
                HeaderFlits(flit)(DataWidth - 1 downto DataWidth/2) := RouterAddress(TargetPEPos, SquareNoCBound);

            elsif HeaderFlitString = "SIZE" then

                HeaderFlits(flit) := std_logic_vector(to_unsigned(PayloadSize, DataWidth));

            elsif HeaderFlitString = "TIME" then

                HeaderFlits(flit) := std_logic_vector(to_unsigned(TimestampFlag, DataWidth));

            elsif HeaderFlitString = "BLNK" then

                HeaderFlits(flit) := (others => '0');

            else

                report "Flit number " & integer'image(flit) & " <" & HeaderFlitString & "> of header of message from PE ID <" & integer'image(SourcePEPos) & "> to PE ID <" & integer'image(TargetPEPos) & "> is not defined" severity error;

            end if;

            --report "        Flit " & integer'image(flit) & " of header of message to be delivered to PE ID " & integer'image(TargetPEsArray(target)) & " is " & HeaderFlitString & " = " & integer'image(to_integer(unsigned(Headers(target, flit)))) severity note;

        end loop BuildFlitLoop;

        return HeaderFlits;

    end function BuildHeader;


    -- Builds payload for each target PE
    function BuildPayload(InjCFG: T_JSON) return DataWidth_vector is

    	constant SourcePEPos: integer := jsonGetInteger(InjCFG, "SourcePEPos");
	    constant TargetPEPos: integer := jsonGetInteger(InjCFG, "TargetPEPos");
	    constant SourceThreadID: integer := jsonGetInteger(InjCFG, "SourceThreadID");
	    constant TargetThreadID: integer := jsonGetInteger(InjCFG, "TargetThreadID");
	    constant AppID: integer := jsonGetInteger(InjCFG, "AppID");
	    constant TargetBaseNoCPos: integer := jsonGetInteger(InjCFG, "TargetBaseNoCPos");

        constant AmountOfMessagesSentFlag: integer := jsonGetInteger(InjCFG, "AmountOfMessagesSentFlag");
	    constant TimestampFlag: integer := jsonGetInteger(InjCFG, "TimestampFlag");

        -- RNG
        variable RNGSeed1: integer := jsonGetInteger(InjCFG, "RNGSeed1");
    	variable RNGSeed2: integer := jsonGetInteger(InjCFG, "RNGSeed2");
        variable RandomNumber: real;

        constant PayloadSize: integer := jsonGetInteger(InjCFG, "PayloadSize");
        variable Payload: DataWidth_vector(0 to PayloadSize - 1);
        variable PayloadFlitString : string(1 to DataWidth/4);

    begin

    	report "Compiling payload for message from PE ID <" & integer'image(SourcePEPos) & "> to PE ID <" & integer'image(TargetPEPos) & ">" severity note;

        BuildFlitLoop: for flit in Payload'range loop 
			
			PayloadFlitString(1 to DataWidth/4) := jsonGetString(InjCFG, "Payload/" & integer'image(flit));

            -- A payload flit can be : "SRCPE" (Source PE position in network), 
            --                         "TGTPE" (Target PE position in network), 
            --                         "APPID" (ID of app being emulated by this injector), 
            --                         "SRCID" (ID of thread being emulated in this PE),
            --                         "TGTID" (ID of target thread ),
            --                         "AVGPT" (Average processing time of a message received by the app being emulated by this PE),
            --                         "TMSTP" (Timestamp of message being sent (to be set in real time, not in this function)),
            --                         "AMMSG" (Amount of messages sent by this PE (also to be se in real time)),
            --                         "RANDO" (Randomize every bit)
            --                         "BLANK" (Fills with zeroes)
            
            if PayloadFlitString(1 to 5) = "SRCPE" then

                Payload(flit) := std_logic_vector(to_unsigned(SourcePEPos, DataWidth));

            elsif PayloadFlitString(1 to 5) = "TGTPE" then

                Payload(flit) := std_logic_vector(to_unsigned(TargetPEPos, DataWidth));

            elsif PayloadFlitString(1 to 5) = "SRCID" then

                Payload(flit) := std_logic_vector(to_unsigned(SourceThreadID, DataWidth));

            elsif PayloadFlitString(1 to 5) = "TGTID" then

                Payload(flit) := std_logic_vector(to_unsigned(TargetThreadID, DataWidth));

            elsif PayloadFlitString(1 to 5) = "APPID" then

                Payload(flit) := std_logic_vector(to_unsigned(AppID, DataWidth));

            elsif PayloadFlitString(1 to 5) = "AVGPT" then

                --Payloads(target, flit) := std_logic_vector(to_unsigned(jsonGetInteger(InjectorJSONConfig, "AverageProcessingTimeInClockPulses"), DataWidth));
                Payload(flit) := (others => '1');

            elsif PayloadFlitString(1 to 5) = "TMSTP" then

                -- Flags for "real time" processing
                Payload(flit) := std_logic_vector(to_unsigned(TimestampFlag, DataWidth));

            elsif PayloadFlitString(1 to 5) = "AMMSG" then 

                -- Flags for "real time" processing
                Payload(flit) := std_logic_vector(to_unsigned(AmountOfMessagesSentFlag, DataWidth));

            elsif PayloadFlitString(1 to 5) = "RANDO" then

                -- Randomizes each bit of current flit
                for i in 0 to DataWidth - 1 loop

                    -- RandomNumber <= (0.0 < RNG < 1.0)
                    Uniform(RNGSeed1, RNGSeed2, RandomNumber);

                    if RandomNumber < 0.5 then

                        Payload(flit)(i) := '0';

                    else

                        Payload(flit)(i) := '1';

                    end if;

                end loop;

            elsif PayloadFlitString(1 to 5) = "BLANK" then

                Payload(flit) := (others=>'0');

            -- Interprets flit as hexadecimal literal
            else

            	Payload(flit) := CONV_DATAWIDTH(PayloadFlitString);
            	--report "Flit number " & integer'image(flit) & " <" & PayloadFlitString & "> of header of message from PE ID <" & integer'image(SourcePEPos) & "> to PE ID <" & integer'image(TargetPEPos) & "> is not defined" severity error;

            end if;
            
        end loop BuildFlitLoop;

        return Payload;

    end function BuildPayload;


end package body Injector_PKG;
