--------------------------------------------------------------------------------
-- Title       : HyHeMPS top level block
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- Authors     : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Top level instantiation of NoC, Buses and Crossbar, as defined
--              in given JSON config file
--------------------------------------------------------------------------------
-- Changelog   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : Add "BridgeBufferSize" to JSON config
--               Map wrapper to last index of its structure instead of 0
--               Add "StandaloneBus" and "StandaloneCrossbar" booleans to JSON config
--               Generalize "BridgeBufferSize" to any size per structure
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library work;
    use work.JSON.all;
    use work.HyHeMPS_PKG.all;


entity HyHeMPS is

    generic (
        PlatformConfigFile: string;
        AmountOfPEs: integer;
        AmountOfNoCNodes: integer
    );
    port (
        Clocks: in std_logic_vector(0 to AmountOfNoCNodes - 1);
        Reset: in std_logic;
        PEInterfaces: inout PEInterface_vector(0 to AmountOfPEs - 1)
    );

end entity HyHeMPS;


architecture RTL of HyHeMPS is

    -- Reads platform JSON config file
    constant PlatCFG: T_JSON := jsonLoad(PlatformConfigFile);
    
    -- Base NoC parameters (from JSON config)
    constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
    constant NoCYSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/1");
    constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
    signal LocalPortInterfaces: PEInterface_vector(0 to AmountOfNoCNodes - 1);
    constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");

    -- Buses Parameters (from JSON config)
    constant AmountOfBuses: integer := jsonGetInteger(PlatCFG, "AmountOfBuses");
    constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
    constant SizeOfLargestBus: integer := jsonGetInteger(PlatCFG, "LargestBus");
    constant BusWrapperIDs: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "BusWrapperIDs");
    constant IsStandaloneBus: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneBus");
    
    subtype BusArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    type BusInterfaces_t is array(natural range <>) of BusArrayOfInterfaces;
    signal BusInterfaces: BusInterfaces_t(0 to AmountOfBuses - 1);

    -- Crossbars Parameters (from JSON config)
    constant AmountOfCrossbars: integer := jsonGetInteger(PlatCFG, "AmountOfCrossbars");
    constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
    constant SizeOfLargestCrossbar: integer := jsonGetInteger(PlatCFG, "LargestCrossbar");
    constant CrossbarWrapperIDs: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "CrossbarWrapperIDs");
    constant IsStandaloneCrossbar: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneCrossbar");
    
    subtype CrossbarArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestCrossbar);
    type CrossbarInterfaces_t is array(natural range <>) of CrossbarArrayOfInterfaces;
    signal CrossbarInterfaces: CrossbarInterfaces_t(0 to AmountOfCrossbars - 1);
    
    -- 
    constant BridgeBufferSize: integer := jsonGetInteger(PlatCFG, "BridgeBufferSize");
    
    -- Reads PE topology information
    constant PEInfo: PEInfo_vector := GetPEInfo(PlatCFG);

begin

    -- Instantiates Hermes NoC, if no standalone structure is to be instantiated
    NoCCond: if (not IsStandaloneBus) and (not IsStandaloneCrossbar) generate
    
        NocGen: entity work.Hermes

            generic map(
                NoCXSize => NoCXSize,
                NoCYSize => NoCYSize
            )
            port map(
                Clocks => Clocks,
                Reset => Reset,
                LocalPortInterfaces => LocalPortInterfaces
            );
    
    end generate NoCCond;
    
    
    -- Instantiate buses, if any are to be instantiated
    BusesCond: if AmountOfBuses > 0 generate

        BusesGen: for i in 0 to AmountOfBuses - 1 generate
            
            subtype BusPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
            type BusPEAddresses_vector is array(natural range <>) of BusPEAddresses_t;
            
            function GetBusPEAddresses(PEInfo: PEInfo_vector) return BusPEAddresses_vector is
                variable BusPEAddresses: BusPEAddresses_vector;
            begin
            
                for i in 0 to AmountOfBuses - 1 loop
                    BusPEAddresses(i) := GetPEAddresses(PlatCFG, PEInfo, "BUS", i);
                end loop;
                
                return BusPEAddresses;
            
            end function GetBusPEAddresses;
            
            constant BusPEAddresses: BusPEAddresses_vector(0 to AmountOfBuses - 1) := GetBusPEAddresses(PEInfo);

        begin
        
            assert false report "Instantiated bus " & integer'image(i) & " with " & integer'image(AmountOfPEsInBuses(i) + 1) & " elements" severity note;

            BusInstance: entity work.HyBus

                generic map(
                    Arbiter          => "RR",
                    AmountOfPEs      => AmountOfPEsInBuses(i) + 1,
                    PEAddresses      => BusPEAddresses(i),
                    BridgeBufferSize => BridgeBufferSize,
                    IsStandalone     => IsStandaloneBus
                )
                port map(
                    Clock        => Clocks(BusWrapperIDs(i)),  -- Clock of its wrapper
                    Reset        => Reset,  -- Global reset, from entity interface
                    PEInterfaces => BusInterfaces(i)
                );

        end generate BusesGen;

    end generate BusesCond;


    -- Instantiate crossbars, if any are to be instantiated
    CrossbarCond: if AmountOfCrossbars > 0 generate

        CrossbarsGen: for i in 0 to AmountOfCrossbars - 1 generate
        
            subtype CrossbarPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
            type CrossbarPEAddresses_vector is array(natural range <>) of CrossbarPEAddresses_t;
            
            function GetCrossbarPEAddresses(PEInfo: PEInfo_vector) return CrossbarPEAddresses_vector is
                variable CrossbarPEAddresses: CrossbarPEAddresses_vector;
            begin
            
                for i in 0 to AmountOfBuses - 1 loop
                    CrossbarPEAddresses(i) := GetPEAddresses(PlatCFG, PEInfo, "XBR", i);
                end loop;
                
                return CrossbarPEAddresses;
            
            end function GetCrossbarPEAddresses;
            
            constant CrossbarPEAddresses: CrossbarPEAddresses_vector(0 to AmountOfCrossbars - 1) := GetCrossbarPEAddresses(PEInfo);
        
        begin

            CrossbarInstance: entity work.Crossbar

                generic map(
                    ArbiterType      => "RR",
                    AmountOfPEs      => AmountOfPEsInCrossbars(i) + 1,
                    PEAddresses      => CrossbarPEAddresses(i),
                    BridgeBufferSize => BridgeBufferSize,
                    IsStandalone     => IsStandaloneCrossbar
                )
                port map(
                    Clock        => Clocks(CrossbarWrapperIDs(i)),  -- Clock of its wrapper
                    Reset        => Reset,  -- Global reset, from entity interface
                    PEInterfaces => CrossbarInterfaces(i)  -- TODO: Map to crossbar interface
                );

            assert false report "Instantiated crossbar " & integer'image(i) & " with " & integer'image(AmountOfPEsInCrossbars(i) + 1) & " elements" severity note;

        end generate CrossbarsGen;

    end generate CrossbarCond;


    -- Connects PE interfaces passed from top entity to local port of routers and into dedicated structures
    PEConnectGen: for i in 0 to AmountOfPEs - 1 generate

        ConnectToNoC: if PEInfo(i).InterfacingStructure = "NOC" generate
            
            -- Input interface of local port of this PE's router
            LocalPortInterfaces(PEInfo(i).PosInStruct).ClockRx <= PEInterfaces(i).ClockTx;
            LocalPortInterfaces(PEInfo(i).PosInStruct).Rx <= PEInterfaces(i).Tx;
            LocalPortInterfaces(PEInfo(i).PosInStruct).DataIn <= PEInterfaces(i).DataOut;
            PEInterfaces(i).CreditI <= LocalPortInterfaces(PEInfo(i).PosInStruct).CreditO;
            
            -- Output interface of local port of this PE's router
            PEInterfaces(i).ClockRx <= LocalPortInterfaces(PEInfo(i).PosInStruct).ClockTx;
            PEInterfaces(i).Rx <= LocalPortInterfaces(PEInfo(i).PosInStruct).Tx;
            PEInterfaces(i).DataIn <= LocalPortInterfaces(PEInfo(i).PosInStruct).DataOut;
            LocalPortInterfaces(PEInfo(i).PosInStruct).CreditI <= PEInterfaces(i).CreditO;

            assert false report "PE ID " & integer'image(i) & " connected to local port of router " & integer'image(WrapperAddresses(i)) severity note;
        
        end generate ConnectToNoC;
        
        ConnectToBus: if PEInfo(i).InterfacingStructure = "BUS" generate
        
            -- Input interface of local port of this PE's bus
            BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockTx <= PEInterfaces(i).ClockTx;
            BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Tx <= PEInterfaces(i).Tx;
            BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataOut <= PEInterfaces(i).DataOut;
            PEInterfaces(i).CreditI <= BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditI;
            
            -- Output interface of local port of this PE's bus
            PEInterfaces(i).ClockRx <= BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockRx;
            PEInterfaces(i).Rx <= BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Rx;
            PEInterfaces(i).DataIn <= BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataIn;
            BusInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditO <= PEInterfaces(i).CreditO;
            
            assert false report "PE ID " & integer'image(i) & " connected to bus " & integer'image(busID(i)) & " at bus position " & integer'image(busPosition(i)) severity note;
        
        end generate ConnectToBus;
        
        ConnectToCrossbar: if PEInfo(i).InterfacingStructure = "XBR" generate
        
            CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockTx <= PEInterfaces(i).ClockTx;
            CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Tx <= PEInterfaces(i).Tx;
            CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataOut <= PEInterfaces(i).DataOut;
            PEInterfaces(i).CreditI <= CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditI;
            
            PEInterfaces(i).ClockRx <= CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockRx;
            PEInterfaces(i).Rx <= CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Rx;
            PEInterfaces(i).DataIn <= CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataIn;
            CrossbarInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditO <= PEInterfaces(i).CreditO;
            
            assert false report "PE ID " & integer'image(i) & " connected to local port of router " & integer'image(WrapperAddresses(i)) severity note;
        
        end generate ConnectToCrossbar;

    end generate PEConnectGen;

end architecture RTL;
