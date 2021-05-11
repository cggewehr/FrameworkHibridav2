--------------------------------------------------------------------------------
-- Title       : HyHeMPS_PKG
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : HyHeMPS_PKG.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Type definitions and JSON translation functions
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : CONV_STRING(int: integer)
--               CONV_INTEGER(str: string)
--------------------------------------------------------------------------------


library IEEE;
    use IEEE.std_Logic_1164.all;
    use IEEE.numeric_std.all;
    
library JSON;
    use JSON.JSON.all;

library Hermes;
    use Hermes.HeMPS_defaults.all;

--library work;
    --use work.HeMPS_defaults.all;
    --use work.JSON.all;


package HyHeMPS_PKG is

    -- Router ports (used as index in router interfaces)
    constant EAST: integer := 0;
    constant WEST: integer := 1;
    constant NORTH: integer := 2;
    constant SOUTH: integer := 3;
    constant LOCAL: integer := 4;

    -- TODO: Use VHDL-2008 package generic feature to set DataWidth dinamically
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

    type PEInputs is record

        -- Input interface
        ClockRx : std_logic;
        Rx      : std_logic;
        DataIn  : DataWidth_t;

        -- Output interface
        CreditI : std_logic;

    end record;

    type PEInputs_vector is array(natural range <>) of PEInputs;

    type PEOutputs is record

        -- Input interface
        CreditO: std_logic;

        -- Output interface
        ClockTx : std_logic;
        Tx      : std_logic;
        DataOut : DataWidth_t;

    end record;

    type PEOutputs_vector is array(natural range <>) of PEOutputs;

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

    -- Coordinate transformations (XY <=> Sequential)
    function PEPosToXY(PEPos: integer; XDim: integer) return HalfDataWidth_t;
    function PEPosFromXY(XY: HalfDataWidth_t; XDim: integer) return integer;

    -- Function declarations for organizing data from JSON config file
    function GetPEInfo(PlatCFG: T_JSON) return PEInfo_vector;
    function GetPEAddresses(PlatCFG: T_JSON; PEInfo: PEInfo_vector; InterfacingStructure: string(1 to 3); StructID: integer) return HalfDataWidth_vector; 
    function GetDefaultPEAddresses(AmountOfPEs: integer) return HalfDataWidth_vector;
    function SetPEAddresses(PEAddressesFromTop: HalfDataWidth_vector; UseDefaultPEAddresses: boolean; AmountOfPEs: integer) return HalfDataWidth_vector;

    -- Misc functions
    procedure UNIFORM(SEED1, SEED2: inout POSITIVE; X: out REAL); -- Used for random number generation
    function incr(value: integer; maxValue: in integer; minValue: in integer) return integer;
    function decr(value: integer; maxValue: in integer; minValue: in integer) return integer;
    function decode(decodeIn: std_logic_vector) return std_logic_vector;

    -- Type conversion functions
    function CONV_INTEGER(bool: boolean) return integer;
    function CONV_DATAWIDTH(str: string) return DataWidth_t;
    -- TODO: CONV_STRING(int: integer)
    -- TODO: CONV_INTEGER(str: string)

end package HyHeMPS_PKG;


package body HyHeMPS_PKG is
    
    -- Translates global address to router xy coordinates (ADAPTED FROM "HeMPS_defaults" PKG)
    function RouterAddress(GlobalAddress: integer; NUMBER_PROCESSORS_X: integer) return HalfDataWidth_t is
            variable posX, posY: QuarterDataWidth_t;
            variable addr: HalfDataWidth_t; 
    begin 

            posX := std_logic_vector(to_unsigned((GlobalAddress mod NUMBER_PROCESSORS_X), QuarterDataWidth));
            posY := std_logic_vector(to_unsigned((GlobalAddress / NUMBER_PROCESSORS_X), QuarterDataWidth));
            
            addr := (posX & posY);

            return addr;

    end function RouterAddress;

    -- Sequential PEPos to XY coords
    function PEPosToXY(PEPos: integer; XDim: integer) return HalfDataWidth_t is begin
        return RouterAddress(PEPos, XDim);
    end function PEPosToXY;

    -- XY coords to sequential PEPos
    function PEPosFromXY(XY: HalfDataWidth_t; XDim: integer) return integer is begin
        return to_integer((unsigned(XY(QuarterDataWidth - 1 downto 0)) * XDim) + unsigned(XY(HalfDataWidth - 1 downto QuarterDataWidth)));
    end function PEPosFromXY;

    -- Returns array of PEInfo structs, containing information about PE relationships to struct
    function GetPEInfo(PlatCFG: T_JSON) return PEInfo_vector is
        
        constant AmountOfPEs: integer := jsonGetInteger(PlatCFG, "AmountOfPEs");
        constant AmountOfBuses: integer := jsonGetInteger(PlatCFG, "AmountOfBuses");
        constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
        constant AmountOfCrossbars: integer := jsonGetInteger(PlatCFG, "AmountOfCrossbars");
        constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
        constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
        constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");
        
        variable PEInfoArray: PEInfo_vector(0 to AmountOfPEs - 1) := (others => (
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
                --PE := jsonGetInteger(PlatCFG, "BusPEIDs/" & "Bus" & to_string(std_logic_vector(to_unsigned(BusID, 32))) & "/" & to_string(PEInBus));
                
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

	-- Returns Amount Of PEs In Struct
    function GetAmountOfPEsInStruct(PlatCFG: T_JSON; InterfacingStructure: string(1 to 3); StructID: integer) return integer is
        variable AmountOfPEsInStruct: integer;  -- Amount of PEs in given struct
    begin
       -- Determine Amount of PEs in given struct
        if InterfacingStructure = "BUS" then
            AmountOfPEsInStruct := jsonGetInteger(PlatCFG, "AmountOfPEsInBuses/" & integer'image(StructID));

        elsif InterfacingStructure = "XBR" then
            AmountOfPEsInStruct := jsonGetInteger(PlatCFG, "AmountOfPEsInCrossbars/" & integer'image(StructID));
        else
            report "Unexpected InterfacingStructure value (GetAmountOfPEsInStruct):" & InterfacingStructure severity failure;
        end if;
        return AmountOfPEsInStruct;
    end function GetAmountOfPEsInStruct;

    -- Returns ID of Wrapper
    function GetWrapperID(PlatCFG: T_JSON; InterfacingStructure: string(1 to 3); StructID: integer) return integer is
        variable WrapperID: integer;  -- Amount of PEs in given struct
    begin
        -- Determine Amount of PEs in given struct
        if InterfacingStructure = "BUS" then
            WrapperID := jsonGetInteger(PlatCFG, "BusWrapperIDs/" & integer'image(StructID));
        elsif InterfacingStructure = "XBR" then
            WrapperID := jsonGetInteger(PlatCFG, "CrossbarWrapperIDs/" & integer'image(StructID));
        else
            report "Unexpected InterfacingStructure value (GetWrapperID):" & InterfacingStructure severity failure;
        end if;
        return WrapperID;
    end function GetWrapperID;
    
    -- Returns PE Addresses in XY form for a given Bus/Crossbar
    function GetPEAddresses(PlatCFG: T_JSON; PEInfo: PEInfo_vector; InterfacingStructure: string(1 to 3); StructID: integer) return HalfDataWidth_vector is
        variable NoCSquareBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
        variable AmountOfPEsInStruct: integer := GetAmountOfPEsInStruct(PlatCFG, InterfacingStructure, StructID);
        variable PEAddresses: HalfDataWidth_vector(0 to AmountOfPEsInStruct);
        variable WrapperID: integer := GetWrapperID(PlatCFG, InterfacingStructure, StructID);
    begin
        
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

    -- Generates random default PE Addresses
    function GetDefaultPEAddresses(AmountOfPEs: integer) return HalfDataWidth_vector is
        variable PEAddresses: HalfDataWidth_vector(0 to AmountOfPEs - 1);
        variable RNGSeed1: positive := 32;
        variable RNGSeed2: positive := 9;
        variable RandomNumber: real;
    begin

        for PE in 0 to AmountOfPEs - 1 loop 
            for i in 0 to HalfDataWidth - 1 loop

                -- Sets 0 < RandomNumber < 1
                UNIFORM(RNGSeed1, RNGSeed2, RandomNumber);

                -- Sets bit based on generated random value
                if RandomNumber > 0.5 then
                    PEAddresses(PE)(i) := '1';
                else
                    PEAddresses(PE)(i) := '0';
                end if;

            end loop;
        end loop;

        return PEAddresses;

    end function GetDefaultPEAddresses;

    -- Returns final PEAddresses array for a Bus/Crossbar, choosing between default randomly generated values or values passed through generic interface
    function SetPEAddresses(PEAddressesFromTop: HalfDataWidth_vector; UseDefaultPEAddresses: boolean; AmountOfPEs: integer) return HalfDataWidth_vector is begin

        if UseDefaultPEAddresses then
            return GetDefaultPEAddresses(AmountOfPEs);
        else
            return PEAddressesFromTop;                                                                               
        end if;

    end function SetPEAddresses;


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


    -- Simple n -> 2**n decoder
    function decode(decodeIn: std_logic_vector) return std_logic_vector is

        constant minValue: unsigned(decodeIn'range) := (others => '0');
        constant maxValue: unsigned(decodeIn'range) := (others => '1');

        variable decodeOut: std_logic_vector(2**decodeIn'length - 1 downto 0) := (others => '0');

    begin

        for i in to_integer(minValue) to to_integer(maxValue) loop 

            if i = unsigned(decodeIn) then

                decodeOut(i) := '1';

            end if;

        end loop;

        return decodeOut;
        
    end function decode;


    function CONV_INTEGER(bool: boolean) return integer is begin

        if bool then
            return 0;
        else
            return 1;
        end if;
        
    end function CONV_INTEGER;


    function CONV_DATAWIDTH(str: string) return DataWidth_t is
        variable slv: DataWidth_t := (others => 'X'); 
    begin 

        for i in str'range loop

            case (str(i)) is

                when '0' => slv(4*(i + 1) downto 4*i + 1) := "0000";
                when '1' => slv(4*(i + 1) downto 4*i + 1) := "0001";
                when '2' => slv(4*(i + 1) downto 4*i + 1) := "0010";
                when '3' => slv(4*(i + 1) downto 4*i + 1) := "0011";
                when '4' => slv(4*(i + 1) downto 4*i + 1) := "0100";
                when '5' => slv(4*(i + 1) downto 4*i + 1) := "0101";
                when '6' => slv(4*(i + 1) downto 4*i + 1) := "0110";
                when '7' => slv(4*(i + 1) downto 4*i + 1) := "0111";
                when '8' => slv(4*(i + 1) downto 4*i + 1) := "1000";
                when '9' => slv(4*(i + 1) downto 4*i + 1) := "1001";
                when 'A' => slv(4*(i + 1) downto 4*i + 1) := "1010";
                when 'B' => slv(4*(i + 1) downto 4*i + 1) := "1011";
                when 'C' => slv(4*(i + 1) downto 4*i + 1) := "1100";
                when 'D' => slv(4*(i + 1) downto 4*i + 1) := "1101";
                when 'E' => slv(4*(i + 1) downto 4*i + 1) := "1110";
                when 'F' => slv(4*(i + 1) downto 4*i + 1) := "1111";
                when others => report "Cant convert <" & str & "> to hexadecimal" severity failure; 

            end case;

        end loop;

        return slv; 

    end CONV_DATAWIDTH;

    -- TODO: CONV_STRING(int: integer)
    -- TODO: CONV_INTEGER(str: string)

end package body HyHeMPS_PKG;
