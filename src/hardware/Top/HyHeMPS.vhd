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

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
    --use work.JSON.all;
    --use work.HyHeMPS_PKG.all;


entity HyHeMPS is

    generic (
        PlatformConfigFile: string;
        AmountOfPEs: integer;
        AmountOfNoCNodes: integer
    );
    port (

        Clocks: in std_logic_vector(0 to AmountOfNoCNodes - 1);
        Reset: in std_logic;

        --PEInterfaces: inout PEInterface_vector(0 to AmountOfPEs - 1)
        PEInputs: out PEInputs_vector(0 to AmountOfPEs - 1);
        PEOutputs: in PEOutputs_vector(0 to AmountOfPEs - 1)
    );

end entity HyHeMPS;


architecture RTL of HyHeMPS is

    -- Reads platform JSON config file
    constant PlatCFG: T_JSON := jsonLoad(PlatformConfigFile);

    -- Reads PE topology information
    constant PEInfo: PEInfo_vector(0 to AmountOfPEs - 1) := GetPEInfo(PlatCFG);
    
    -- Base NoC parameters (from JSON config)
    constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
    constant NoCYSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/1");
    constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
    --signal LocalPortInterfaces: PEInterface_vector(0 to AmountOfNoCNodes - 1);
    signal LocalPortInputs: PEOutputs_vector(0 to AmountOfNoCNodes - 1);
    signal LocalPortOutputs: PEInputs_vector(0 to AmountOfNoCNodes - 1);
    constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");

    -- Buses Parameters (from JSON config)
    constant AmountOfBuses: integer := jsonGetInteger(PlatCFG, "AmountOfBuses");
    constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
    constant SizeOfLargestBus: integer := jsonGetInteger(PlatCFG, "LargestBus");
    constant BusWrapperIDs: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "BusWrapperIDs");
    constant IsStandaloneBus: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneBus");
    
    --subtype BusArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    subtype BusArrayOfInputInterfaces is PEInputs_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    subtype BusArrayOfOutputInterfaces is PEOutputs_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    --type BusInterfaces_t is array(natural range <>) of BusArrayOfInterfaces;
    type BusInputInterfaces_t is array(natural range <>) of BusArrayOfInputInterfaces;
    type BusOutputInterfaces_t is array(natural range <>) of BusArrayOfOutputInterfaces;
    --signal BusInterfaces: BusInterfaces_t(0 to AmountOfBuses - 1);
    signal BusInputInterfaces: BusOutputInterfaces_t(0 to AmountOfBuses - 1);
    signal BusOutputInterfaces: BusInputInterfaces_t(0 to AmountOfBuses - 1);

    subtype BusPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    type BusPEAddresses_vector is array(natural range <>) of BusPEAddresses_t;
    
    function GetBusPEAddresses(PEInfo: PEInfo_vector) return BusPEAddresses_vector is
        variable BusPEAddresses: BusPEAddresses_vector(0 to AmountOfBuses - 1);
    begin
    
        for i in 0 to AmountOfBuses - 1 loop
            BusPEAddresses(i) := GetPEAddresses(PlatCFG, PEInfo, "BUS", i);
        end loop;
        
        return BusPEAddresses;
    
    end function GetBusPEAddresses;
    
    constant BusPEAddresses: BusPEAddresses_vector(0 to AmountOfBuses - 1) := GetBusPEAddresses(PEInfo);

    -- Crossbars Parameters (from JSON config)
    constant AmountOfCrossbars: integer := jsonGetInteger(PlatCFG, "AmountOfCrossbars");
    constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
    constant SizeOfLargestCrossbar: integer := jsonGetInteger(PlatCFG, "LargestCrossbar");
    constant CrossbarWrapperIDs: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "CrossbarWrapperIDs");
    constant IsStandaloneCrossbar: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneCrossbar");
    
    --subtype CrossbarArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    subtype CrossbarArrayOfInputInterfaces is PEInputs_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    subtype CrossbarArrayOfOutputInterfaces is PEOutputs_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    --type CrossbarInterfaces_t is array(natural range <>) of CrossbarArrayOfInterfaces;
    type CrossbarInputInterfaces_t is array(natural range <>) of CrossbarArrayOfInputInterfaces;
    type CrossbarOutputInterfaces_t is array(natural range <>) of CrossbarArrayOfOutputInterfaces;
    --signal CrossbarInterfaces: CrossbarInterfaces_t(0 to AmountOfCrossbars - 1);
    signal CrossbarInputInterfaces: CrossbarOutputInterfaces_t(0 to AmountOfCrossbars - 1);
    signal CrossbarOutputInterfaces: CrossbarInputInterfaces_t(0 to AmountOfCrossbars - 1);

    subtype CrossbarPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    type CrossbarPEAddresses_vector is array(natural range <>) of CrossbarPEAddresses_t;
    
    function GetCrossbarPEAddresses(PEInfo: PEInfo_vector) return CrossbarPEAddresses_vector is
        variable CrossbarPEAddresses: CrossbarPEAddresses_vector(0 to AmountOfCrossbars - 1);
    begin
    
        for i in 0 to AmountOfCrossbars - 1 loop
            CrossbarPEAddresses(i) := GetPEAddresses(PlatCFG, PEInfo, "XBR", i);
        end loop;
        
        return CrossbarPEAddresses;
    
    end function GetCrossbarPEAddresses;
    
    constant CrossbarPEAddresses: CrossbarPEAddresses_vector(0 to AmountOfCrossbars - 1) := GetCrossbarPEAddresses(PEInfo);
    
    -- 
    constant BridgeBufferSize: integer := jsonGetInteger(PlatCFG, "BridgeBufferSize");
    
    -- Reads PE topology information
    --constant PEInfo: PEInfo_vector(0 to AmountOfPEs - 1) := GetPEInfo(PlatCFG);

begin

    -- Instantiates Hermes NoC, if no standalone structure is to be instantiated
    NoCCond: if (not IsStandaloneBus) and (not IsStandaloneCrossbar) generate
    
        NoCGen: entity work.Hermes

            generic map(
                NoCXSize => NoCXSize,
                NoCYSize => NoCYSize
            )
            port map(
                Clocks => Clocks,
                Reset => Reset,
                --LocalPortInterfaces => LocalPortInterfaces
                PEInputs => LocalPortOutputs,
                PEOutputs => LocalPortInputs
            );
    
    end generate NoCCond;
    
    
    -- Instantiate buses, if any are to be instantiated
    BusesCond: if AmountOfBuses > 0 generate

        BusesGen: for i in 0 to AmountOfBuses - 1 generate 
        
            BusInstance: entity work.HyBus

                generic map(
                    Arbiter          => "RR",
                    --AmountOfPEs      => (AmountOfPEsInBuses(i) + 1),  -- TODO: Not add +1 if standalone
                    AmountOfPEs      => (AmountOfPEsInBuses(i) + boolToInt(IsStandaloneBus)),
                    PEAddresses      => BusPEAddresses(i),
                    BridgeBufferSize => BridgeBufferSize,
                    IsStandalone     => IsStandaloneBus
                )
                port map(
                    Clock        => Clocks(BusWrapperIDs(i)),  -- Clock of its wrapper
                    Reset        => Reset,  -- Global reset, from entity interface
                    --PEInterfaces => BusInterfaces(i)
                    PEInputs => BusOutputInterfaces(i),
                    PEOutputs => BusInputInterfaces(i)
                );

            assert false report "Instantiated Bus <" & integer'image(i) & "> with <" & integer'image(AmountOfPEsInBuses(i) + boolToInt(IsStandaloneBus)) & "> elements" severity note;

            -- Connect Bus to base NoC. (Wrapper is at the highest index, obtained by AmountOfPEsInBuses(i))
            ConnectBusToBaseNoC: if not IsStandaloneBus generate

                -- CrossbarInputInterfaces(i) = PEInputs
                -- LocalPortOutputs(i) = PEInputs

                -- NoC to Bus (Bus <= NoC)
                BusInputInterfaces(i)(AmountOfPEsInBuses(i)).ClockTx <= LocalPortOutputs(BusWrapperIDs(i)).ClockRx; 
                BusInputInterfaces(i)(AmountOfPEsInBuses(i)).Tx <= LocalPortOutputs(BusWrapperIDs(i)).Rx;
                BusInputInterfaces(i)(AmountOfPEsInBuses(i)).DataOut <= LocalPortOutputs(BusWrapperIDs(i)).DataIn;
                LocalPortInputs(BusWrapperIDs(i)).CreditO <= BusOutputInterfaces(i)(AmountOfPEsInBuses(i)).CreditI;

                -- Bus to NoC
                LocalPortInputs(BusWrapperIDs(i)).ClockTx <= BusOutputInterfaces(i)(AmountOfPEsInBuses(i)).ClockRx;
                LocalPortInputs(BusWrapperIDs(i)).Tx <= BusOutputInterfaces(i)(AmountOfPEsInBuses(i)).Rx;
                LocalPortInputs(BusWrapperIDs(i)).DataOut <= BusOutputInterfaces(i)(AmountOfPEsInBuses(i)).DataIn;
                BusInputInterfaces(i)(AmountOfPEsInBuses(i)).CreditO <= LocalPortOutputs(BusWrapperIDs(i)).CreditI;

                assert false report "Connected Bus <" & integer'image(i) & "> to base NoC router <" & integer'image(BusWrapperIDs(i)) & ">'s local port" severity note;

            end generate ConnectBusToBaseNoC;

        end generate BusesGen;

    end generate BusesCond;


    -- Instantiate crossbars, if any are to be instantiated
    CrossbarCond: if AmountOfCrossbars > 0 generate

        CrossbarsGen: for i in 0 to AmountOfCrossbars - 1 generate

            -- Instantiate Crossbar
            CrossbarInstance: entity work.Crossbar

                generic map(
                    ArbiterType      => "RR",
                    --AmountOfPEs      => (AmountOfPEsInCrossbars(i) + 1),  -- TODO: Not add +1 if standalone
                    AmountOfPEs      => (AmountOfPEsInCrossbars(i) + boolToInt(IsStandaloneCrossbar)),
                    PEAddresses      => CrossbarPEAddresses(i),
                    BridgeBufferSize => BridgeBufferSize,
                    IsStandalone     => IsStandaloneCrossbar
                )
                port map(
                    Clock        => Clocks(CrossbarWrapperIDs(i)),  -- Clock of its wrapper
                    Reset        => Reset,  -- Global reset, from entity interface
                    --PEInterfaces => CrossbarInterfaces(i)
                    PEInputs => CrossbarOutputInterfaces(i),
                    PEOutputs => CrossbarInputInterfaces(i)
                );
            
            assert false report "Instantiated Crossbar <" & integer'image(i) & "> with <" & integer'image(AmountOfPEsInCrossbars(i) + boolToInt(IsStandaloneCrossbar)) & "> elements" severity note;

            -- Connects Crossbar to base NoC. (Wrapper is at the highest index, obtained by AmountOfPEsInCrossbars(i))
            ConnectCrossbarToBaseNoC: if not IsStandaloneCrossbar generate

                -- CrossbarInputInterfaces(i) = PEInputs
                -- LocalPortOutputs(i) = PEInputs

                -- NoC to Crossbar (Crossbar <= NoC)
                CrossbarInputInterfaces(i)(AmountOfPEsInCrossbars(i)).ClockTx <= LocalPortOutputs(CrossbarWrapperIDs(i)).ClockRx; 
                CrossbarInputInterfaces(i)(AmountOfPEsInCrossbars(i)).Tx <= LocalPortOutputs(CrossbarWrapperIDs(i)).Rx;
                CrossbarInputInterfaces(i)(AmountOfPEsInCrossbars(i)).DataOut <= LocalPortOutputs(CrossbarWrapperIDs(i)).DataIn;
                LocalPortInputs(CrossbarWrapperIDs(i)).CreditO <= CrossbarOutputInterfaces(i)(AmountOfPEsInCrossbars(i)).CreditI;

                -- Crossbar to NoC
                LocalPortInputs(CrossbarWrapperIDs(i)).ClockTx <= CrossbarOutputInterfaces(i)(AmountOfPEsInCrossbars(i)).ClockRx;
                LocalPortInputs(CrossbarWrapperIDs(i)).Tx <= CrossbarOutputInterfaces(i)(AmountOfPEsInCrossbars(i)).Rx;
                LocalPortInputs(CrossbarWrapperIDs(i)).DataOut <= CrossbarOutputInterfaces(i)(AmountOfPEsInCrossbars(i)).DataIn;
                CrossbarInputInterfaces(i)(AmountOfPEsInCrossbars(i)).CreditO <= LocalPortOutputs(CrossbarWrapperIDs(i)).CreditI;

                assert false report "Connected Crossbar <" & integer'image(i) & "> to base NoC router <" & integer'image(CrossbarWrapperIDs(i)) & ">'s local port" severity note;

            end generate ConnectCrossbarToBaseNoC;

        end generate CrossbarsGen;

    end generate CrossbarCond;


    -- Connects PE interfaces passed from top entity to local port of routers and into dedicated structures
    PEConnectGen: for i in 0 to AmountOfPEs - 1 generate

        ConnectToNoC: if PEInfo(i).InterfacingStructure = "NOC" generate
            
            -- Input interface of local port of this PE's router
            LocalPortInputs(PEInfo(i).PosInStruct).ClockTx <= PEOutputs(i).ClockTx;
            LocalPortInputs(PEInfo(i).PosInStruct).Tx <= PEOutputs(i).Tx;
            LocalPortInputs(PEInfo(i).PosInStruct).DataOut <= PEOutputs(i).DataOut;
            PEInputs(i).CreditI <= LocalPortOutputs(PEInfo(i).PosInStruct).CreditI;
            
            -- Output interface of local port of this PE's router
            PEInputs(i).ClockRx <= LocalPortOutputs(PEInfo(i).PosInStruct).ClockRx;
            PEInputs(i).Rx <= LocalPortOutputs(PEInfo(i).PosInStruct).Rx;
            PEInputs(i).DataIn <= LocalPortOutputs(PEInfo(i).PosInStruct).DataIn;
            LocalPortInputs(PEInfo(i).PosInStruct).CreditO <= PEOutputs(i).CreditO;

            assert false report "PE ID <" & integer'image(i) & "> connected to local port of router <" & integer'image(WrapperAddresses(i)) & ">" severity note;
        
        end generate ConnectToNoC;
        
        ConnectToBus: if PEInfo(i).InterfacingStructure = "BUS" generate
        
            -- Input interface of local port of this PE's bus
            BusInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockTx <= PEOutputs(i).ClockTx;
            BusInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Tx <= PEOutputs(i).Tx;
            BusInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataOut <= PEOutputs(i).DataOut;
            PEInputs(i).CreditI <= BusOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditI;
            
            -- Output interface of local port of this PE's bus
            PEInputs(i).ClockRx <= BusOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockRx;
            PEInputs(i).Rx <= BusOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Rx;
            PEInputs(i).DataIn <= BusOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataIn;
            BusInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditO <= PEOutputs(i).CreditO;
            
            assert false report "PE ID <" & integer'image(i) & "> connected to bus <" & integer'image(PEInfo(i).StructID) & "> at bus position <" & integer'image(PEInfo(i).PosInStruct) & ">" severity note;
        
        end generate ConnectToBus;
        
        ConnectToCrossbar: if PEInfo(i).InterfacingStructure = "XBR" generate
        
            CrossbarInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockTx <= PEOutputs(i).ClockTx;
            CrossbarInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Tx <= PEOutputs(i).Tx;
            CrossbarInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataOut <= PEOutputs(i).DataOut;
            PEInputs(i).CreditI <= CrossbarOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditI;
            
            PEInputs(i).ClockRx <= CrossbarOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).ClockRx;
            PEInputs(i).Rx <= CrossbarOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).Rx;
            PEInputs(i).DataIn <= CrossbarOutputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).DataIn;
            CrossbarInputInterfaces(PEInfo(i).StructID)(PEInfo(i).PosInStruct).CreditO <= PEOutputs(i).CreditO;
            
            assert false report "PE ID <" & integer'image(i) & "> connected to crossbar <" & integer'image(PEInfo(i).StructID) & "> at crossbar position <" & integer'image(PEInfo(i).PosInStruct) & ">" severity note;
        
        end generate ConnectToCrossbar;

        -- Makes sure PE InterfacingStructure value is coherent
        assert not (PEInfo(i).InterfacingStructure /= "NOC" and PEInfo(i).InterfacingStructure /= "BUS" and PEInfo(i).InterfacingStructure /= "XBR") report "PEInfo(" & integer'image(i) & ").InterfacingStructure value <" & PEInfo(i).InterfacingStructure & "> not recognized" severity failure;

    end generate PEConnectGen;

end architecture RTL;
