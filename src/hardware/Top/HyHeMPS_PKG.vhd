--------------------------------------------------------------------------
-- Package containing JSON translation functions and basic type definitions
--------------------------------------------------------------------------

library IEEE;
    use IEEE.std_Logic_1164.all;
    use IEEE.numeric_std.all;
    
library work;
    use work.HeMPS_defaults.all;
    use work.JSON.all;

package HyHeMPS_PKG is

    -- Router ports (used as index in router interfaces)
    constant EAST: integer := 0;
    constant WEST: integer := 1;
    constant NORTH: integer := 2;
    constant SOUTH: integer := 3;
    constant LOCAL: integer := 4;

    constant DataWidth: integer := 32; 
    constant HalfDataWidth: integer := DataWidth/2;
    constant QuarterDataWidth: integer := DataWidth/4;

    subtype DataWidth_t is std_logic_vector(DataWidth - 1 downto 0);
    subtype HalfDataWidth_t is std_logic_vector(HalfDataWidth - 1 downto 0);
    subtype QuarterDataWidth_t is std_logic_vector(QuarterDataWidth - 1 downto 0);

    type DataWidth_vector is array(natural range <>) of DataWidth_t;
    type HalfDataWidth_vector is array(natural range <>) of HalfDataWidth_t;
    type QuarterDataWidth_vector is array(natural range <>) of QuarterDataWidth_t;

    -- Typedefs for headers and payloads
    type HeaderFlits_t is array(integer range <>, integer range <>) of DataWidth_t;
    type PayloadFlits_t is array(integer range <>, integer range <>) of DataWidth_t;

    -- 
    type PEInterface is record

        -- Basic
        --Clock   : std_logic;
        Reset   : std_logic;

        -- Input interface
        ClockRx : std_logic;
        Rx      : std_logic;
        DataIn  : DataWidth_t;
        CreditO : std_logic;

        -- Output interface
        ClockTx : std_logic;
        Tx      : std_logic;
        DataOut : DataWidth_t;
        CreditI : std_logic;

    end record PEInterface;

    type PEInterface_vector is array(natural range <>) of PEInterface;

    -- 
    type RouterInterface is record
    
        -- Input Interface
        ClockRx: regNport;
        Rx:      regNport;
        DataIn:  arraynport_regflit;
        CreditO: regNport;

        -- Output Interface    
        ClockTx: regNport;
        Tx:      regNport;
        DataOut: arraynport_regflit;
        CreditI: regNport;

    end record RouterInterface;

    type RouterInterface_vector is array(natural range <>) of RouterInterface;
    
    type PEInfo is record
    
        InterfacingStructure: string(1 to 3);
        StructID: integer;
        PosInStruct: integer;
        XYAddress: HalfDataWidth_t;
        
    end record;
    
    type PEInfo_vector is array(natural range <>) of PEInfo;

    -- Adapted functions from HeMPS_defaults
    function RouterAddress(GlobalAddress: integer; NUMBER_PROCESSORS_X: integer) return HalfDataWidth_t;

    -- Function declarations for organizing data from JSON config file
    function FillTargetMessageSizeArray(TargetPayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector;
    function FillSourceMessageSizeArray(SourcePayloadSizeArray: integer_vector; HeaderSize: integer) return integer_vector;
    --function FillWrapperAddressTableArray(PlatformJSONConfig: T_JSON; TargetPEsArray: integer_vector) return integer_vector;
    function FindMaxPayloadSize(TargetPayloadSizeArray: integer_vector) return integer;
    function BuildHeaders(InjCFG: T_JSON; PlatCFG: T_JSON; HeaderSize: integer; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return HeaderFlits_t;
    function BuildPayloads(InjCFG: T_JSON; TargetPayloadSizeArray: integer_vector; TargetPEsArray: integer_vector) return PayloadFlits_t;
    function GetPEInfo(PlatCFG: T_JSON) return PEInfo_vector;
    function GetPEAddresses(PlatCFG: T_JSON; PEInfo: PEInfo_vector; InterfacingStructure: string(1 to 3); StructID: integer) return HalfDataWidth_vector; 

    -- Misc functions
    procedure UNIFORM (SEED1, SEED2 : inout POSITIVE; X : out REAL); -- Used for random number generation
    function incr(value: integer; maxValue: in integer; minValue: in integer) return integer;
    function decr(value: integer; maxValue: in integer; minValue: in integer) return integer;

end package HyHeMPS_PKG;


package body HyHeMPS_PKG is


    -- Translates global address to router xy coordinates (ADAPTED FROM "HeMPS_defaults" PKG)
    function RouterAddress(GlobalAddress: integer ; NUMBER_PROCESSORS_X: integer) return HalfDataWidth_t is
            variable posX, posY: QuarterDataWidth_t;
            variable addr: HalfDataWidth_t; 
    begin 

            posX := std_logic_vector(to_unsigned((GlobalAddress mod NUMBER_PROCESSORS_X), QuarterDataWidth));
            posY := std_logic_vector(to_unsigned((GlobalAddress / NUMBER_PROCESSORS_X), QuarterDataWidth));
            
            addr := (posX & posY);

            return addr;

    end function RouterAddress;


    -- Fills array of source message size for each source PE
    function FillSourceMessageSizeArray(SourcePayloadSizeArray: integer_vector ; HeaderSize: integer) return integer_vector is
        variable SourceMessageSizeArray : integer_vector(SourcePayloadSizeArray'range);
    begin

        FillSourceMessageSizeLoop: for i in SourcePayloadSizeArray'range loop 
            SourceMessageSizeArray(i) := SourcePayloadSizeArray(i) + HeaderSize;
        end loop FillSourceMessageSizeLoop;

        return SourceMessageSizeArray;

    end function;


    -- Fills array of target message size (Payload + Header) for each target PE
    function FillTargetMessageSizeArray(TargetPayloadSizeArray: integer_vector ; HeaderSize: integer) return integer_vector is
        variable TargetMessageSizeArray: integer_vector(TargetPayloadSizeArray'range);
    begin

        FillTargetMessageSizeLoop : for i in TargetPayloadSizeArray'range loop
            TargetMessageSizeArray(i) := TargetPayloadSizeArray(i) + HeaderSize;
        end loop;
        
        return TargetMessageSizeArray;
        
    end function FillTargetMessageSizeArray;


    -- Fills array containing address of associated wrapper for each global address (To find the address of a global address's associated wrapper)
    function FillWrapperAddressTableArray(PlatformJSONConfig: T_JSON ; TargetPEsArray: integer_vector) return integer_vector is
        variable WrapperAddressTableArray: integer_vector(TargetPEsArray'range);
    begin

        FillWrapperAddressTableArrayLoop: for i in TargetPEsArray'range loop
            WrapperAddressTableArray(i) := jsonGetInteger(PlatformJSONConfig, ("WrapperAddresses/" & integer'image(TargetPEsArray(i))));
        end loop FillWrapperAddressTableArrayLoop;

        return WrapperAddressTableArray;

    end function FillWrapperAddressTableArray;


    -- Builds header for each target PE
    function BuildHeaders(InjCFG: T_JSON ; PlatCFG: T_JSON ; HeaderSize: integer ; TargetPayloadSizeArray: integer_vector ; TargetPEsArray: integer_vector) return HeaderFlits_t is
        
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
    function BuildPayloads(InjCFG: T_JSON ; TargetPayloadSizeArray: integer_vector ; TargetPEsArray: integer_vector) return PayloadFlits_t is

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
    function FindMaxPayloadSize(TargetPayloadSizeArray : integer_vector) return integer is
        variable MaxPayloadSize : integer := 0;
    begin

        FindMaxPayloadSizeLoop : for i in TargetPayloadSizeArray'range loop
            
            if TargetPayloadSizeArray(i) > MaxPayloadSize then

                MaxPayloadSize := TargetPayloadSizeArray(i);

            end if;

        end loop FindMaxPayloadSizeLoop;

        return MaxPayloadSize;

    end function FindMaxPayloadSize;
    
    
    function GetPEInfo(PlatCFG: T_JSON) return PEInfo_vector is
        
        constant AmountOfPEs: integer := jsonGetInteger(PlatCFG, "AmountOfPEs");
        constant AmountOfBuses: integer := jsonGetInteger(PlatCFG, "AmountOfBuses");
        constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
        constant AmountOfCrossbars: integer := jsonGetInteger(PlatCFG, "AmountOfCrossbars");
        constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
        constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
        constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");
        
        variable PEInfoArray: PEInfo_vector := (others => (
            InterfacingStructure => "NUL",
            StructID => -1,
            PosInStruct => -1,
            XYAddress => (others => '1')
        ));
        
        variable PE: integer;

    begin
    
        -- Loop through every bus
        for BusID in 0 to AmountOfBuses - 1 loop
        
            -- Loop through every PE in current bus
            for PEInBus in 0 to AmountOfPEsInBuses(BusID) - 1 loop
            
                PE := jsonGetInteger(PlatCFG, "BusPEIDs/" & "Bus" & integer'image(BusID) & "/" & integer'image(PEInBus));
                
                PEInfoArray(PE).InterfacingStructure := "BUS";
                PEInfoArray(PE).StructID := BusID;
                PEInfoArray(PE).PosInStruct := PEInBus;
                PEInfoArray(PE).XYAddress := RouterAddress(PE, SquareNoCBound);
                
            end loop; 
        
        end loop;
        
        -- Loop through every crossbar
        for CrossbarID in 0 to AmountOfCrossbars - 1 loop
        
            -- Loop through every PE in current crossbar
            for PEInCrossbar in 0 to AmountOfPEsInCrossbars(CrossbarID) - 1 loop
            
                PE := jsonGetInteger(PlatCFG, "CrossbarPEIDs/" & "Crossbar" & integer'image(CrossbarID) & "/" & integer'image(PEInCrossbar));
                
                PEInfoArray(PE).InterfacingStructure := "XBR";
                PEInfoArray(PE).StructID := CrossbarID;
                PEInfoArray(PE).PosInStruct := PEInCrossbar;
                PEInfoArray(PE).XYAddress := RouterAddress(PE, SquareNoCBound);
                
            end loop; 
        
        end loop;  
        
        -- Loop through every PE
        for PE in 0 to AmountOfPEs - 1 loop
        
            -- Checks if this PE has already been processed. If so, skips to next loop iteration
            if PEInfoArray(PE).InterfacingStructure /= "NUL" then
                next;
                
            else
                
                PEInfoArray(PE).InterfacingStructure := "NOC";
                PEInfoArray(PE).StructID := WrapperAddresses(PE);
                PEInfoArray(PE).PosInStruct := WrapperAddresses(PE);
                PEInfoArray(PE).XYAddress := RouterAddress(PE, SquareNoCBound);
                
            end if;
            
        end loop;
        
        return PEInfoArray;
    
    end function GetPEInfo;
    
    
    function GetPEAddresses(PlatCFG: T_JSON; PEInfo: PEInfo_vector; InterfacingStructure: string(1 to 3); StructID: integer) return HalfDataWidth_vector is
        variable NoCSquareBound: integer := jsonGetInteger(PlatCFG, "NoCSquareBound");
        variable PEAddresses: HalfDataWidth_vector;
        variable AmountOfPEsInStruct: integer;  -- Amount of PEs in given struct
        variable WrapperID: integer;            -- ADDR of wrapper of this struct in base NoC
    begin
    
        -- Determine Amount of PEs in given struct
        if InterfacingStructure = "BUS" then
            AmountOfPEsInStruct := jsonGetInteger(PlatCFG, "AmountOfPEsInBuses/" & integer'image(StructID));
            WrapperID := jsonGetInteger(PlatCFG, "BusWrapperIDs/" & integer'image(StructID));
        elsif InterfacingStructure = "XBR" then
            AmountOfPEsInStruct := jsonGetInteger(PlatCFG, "AmountOfPEsInCrossbars/" & integer'image(StructID));
            WrapperID := jsonGetInteger(PlatCFG, "CrossbarWrapperIDs/" & integer'image(StructID));
        else
            report "Unexpected InterfacingStructure value:" & InterfacingStructure severity failure;
        end if;
            
        -- Set PE addresses
        for i in PEInfo'range loop
        
            if PEInfo(i).InterfacingStructure = InterfacingStructure and PEInfo(i).StructID = StructID then
            
                PEAddresses(PEInfo(i).PosInStruct) := PEInfo(i).XYAddress;
            
            end if;
        
        end loop;
        
        -- Set Wrapper address at the end of array being returned
        PEAddresses(AmountOfPEsInStruct) := RouterAddress(WrapperID, NoCSquareBound);
        
        return PEAddresses;
    
    end function GetPEAddresses;


    -- Borrowed from GHDL ieee.math_real implementation (https://github.com/ghdl/ghdl/blob/master/libraries/openieee/math_real-body.vhdl)
    -- Returns a pseudo-random value between 0 and 1 (Algorithm from: Pierre L'Ecuyer, CACM June 1988 Volume 31 Number 6 page 747 figure 3)
    procedure UNIFORM(SEED1, SEED2: inout POSITIVE; X: out REAL) is
        variable z, k: integer;
        variable s1, s2: integer;
    begin

        k := seed1 / 53668;
        s1 := 40014 * (seed1 - k * 53668) - k * 12211;

        if s1 < 0 then
            seed1 := s1 + 2147483563;
        else
            seed1 := s1;
        end if;

        k := seed2 / 52774;
        s2 := 40692 * (seed2 - k * 52774) - k * 3791;

        if s2 < 0 then
            seed2 := s2 + 2147483399;
        else
            seed2 := s2;
        end if;

        z := seed1 - seed2;

        if z < 1 then
            z := z + 2147483562;
        end if;

        x := real(z) * 4.656613e-10;

    end procedure UNIFORM;


    -- Simple increment and wrap around
    function incr(value: integer ; maxValue: in integer ; minValue: in integer) return integer is

    begin

        if value = maxValue then
            return minValue;
        else
            return value + 1;
        end if;

    end function incr;


    -- Simple decrement and wrap around
    function decr(value: integer ; maxValue: in integer ; minValue: in integer) return integer is

    begin

        if value = minValue then
            return maxValue;
        else
            return value - 1;
        end if;

    end function decr;


end package body HyHeMPS_PKG;
