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

    -- Reads PE topology information (from JSON config)
    constant PEInfo: PEInfo_vector(0 to AmountOfPEs - 1) := GetPEInfo(PlatCFG);

    -- Buffer size for Bus/Crossbar bridges (NoC buffer size is defined statically as 4 in HeMPS_defaults)
    constant BridgeBufferSize: integer := jsonGetInteger(PlatCFG, "BridgeBufferSize");
    
    -- Base NoC parameters (from JSON config)
    constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
    constant NoCYSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/1");
    constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
    constant WrapperAddresses: integer_vector(0 to AmountOfPEs - 1) := jsonGetIntegerArray(PlatCFG, "WrapperAddresses");

    -- Base NoC interface
    signal RouterClocks: std_logic_vector(0 to AmountOfNoCNodes - 1);
    signal LocalPortInputs: PEOutputs_vector(0 to AmountOfNoCNodes - 1);
    signal LocalPortOutputs: PEInputs_vector(0 to AmountOfNoCNodes - 1);

    -- Bus Parameters (from JSON config)
    constant AmountOfBuses: integer := jsonGetInteger(PlatCFG, "AmountOfBuses");
    --constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
    constant SizeOfLargestBus: integer := jsonGetInteger(PlatCFG, "LargestBus");
    --constant BusWrapperIDs: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "BusWrapperIDs");
    constant IsStandaloneBus: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneBus");
    
    -- Bus interfaces
    signal BusClocks: std_logic_vector(0 to AmountOfBuses - 1);
    --subtype BusArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    subtype BusArrayOfInputInterfaces is PEInputs_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    subtype BusArrayOfOutputInterfaces is PEOutputs_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
    --type BusInterfaces_t is array(natural range <>) of BusArrayOfInterfaces;
    type BusInputInterfaces_t is array(natural range <>) of BusArrayOfInputInterfaces;
    type BusOutputInterfaces_t is array(natural range <>) of BusArrayOfOutputInterfaces;
    --signal BusInterfaces: BusInterfaces_t(0 to AmountOfBuses - 1);
    signal BusInputInterfaces: BusOutputInterfaces_t(0 to AmountOfBuses - 1);
    signal BusOutputInterfaces: BusInputInterfaces_t(0 to AmountOfBuses - 1);

    -- Crossbars Parameters (from JSON config)
    constant AmountOfCrossbars: integer := jsonGetInteger(PlatCFG, "AmountOfCrossbars");
    --constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
    constant SizeOfLargestCrossbar: integer := jsonGetInteger(PlatCFG, "LargestCrossbar");
    --constant CrossbarWrapperIDs: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "CrossbarWrapperIDs");
    constant IsStandaloneCrossbar: boolean := jsonGetBoolean(PlatCFG, "IsStandaloneCrossbar");
    
    -- Crossbar interfaces
    signal CrossbarClocks: std_logic_vector(0 to AmountOfCrossbars - 1);
    --subtype CrossbarArrayOfInterfaces is PEInterface_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    subtype CrossbarArrayOfInputInterfaces is PEInputs_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    subtype CrossbarArrayOfOutputInterfaces is PEOutputs_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
    --type CrossbarInterfaces_t is array(natural range <>) of CrossbarArrayOfInterfaces;
    type CrossbarInputInterfaces_t is array(natural range <>) of CrossbarArrayOfInputInterfaces;
    type CrossbarOutputInterfaces_t is array(natural range <>) of CrossbarArrayOfOutputInterfaces;
    --signal CrossbarInterfaces: CrossbarInterfaces_t(0 to AmountOfCrossbars - 1);
    signal CrossbarInputInterfaces: CrossbarOutputInterfaces_t(0 to AmountOfCrossbars - 1);
    signal CrossbarOutputInterfaces: CrossbarInputInterfaces_t(0 to AmountOfCrossbars - 1);

    -- DVFS parameters (from JSON config)
    constant DVFSEnable: boolean := jsonGetBoolean(PlatCFG, "DVFSEnable");
    constant DVFSServiceID: DataWidth_t := CONV_DATAWIDTH(jsonGetString(PlatCFG, "DVFSServiceID"));
    constant DVFSAmountOfVoltageLevels: integer := jsonGetInteger(PlatCFG, "DVFSAmountOfVoltageLevels");
    constant DVFSCounterResolution: integer := jsonGetInteger(PlatCFG, "DVFSCounterResolution");

    -- DVFS interfaces
    subtype DVFSSwitchEnables_t is std_logic_vector(0 to DVFSAmountOfVoltageLevels - 1);
    type DVFSSwitchEnables_vector is array(natural range <>) of DVFSSwitchEnables_t;
    signal DVFSRouterSwitchEnables: DVFSSwitchEnables_vector(0 to AmountOfNoCNodes - 1);
    signal DVFSBusSwitchEnables: DVFSSwitchEnables_vector(0 to AmountOfBuses - 1);
    signal DVFSCrossbarSwitchEnables: DVFSSwitchEnables_vector(0 to AmountOfCrossbars - 1);

begin

    -- Instantiates Hermes NoC, if no standalone structure is to be instantiated
    NoCCond: if (not IsStandaloneBus) and (not IsStandaloneCrossbar) generate
        
        -- Instantiates a DVFS controller for every router
        DVFSCond: if DVFSEnable generate

            NoCDVFSControllers: for i in 0 to AmountOfNoCNodes - 1 generate

                DVFSController: entity work.DVFSController

                    generic map(
                        DVFSServiceCode => DVFSServiceID,
                        AmountOfVoltageLevels => DVFSAmountOfVoltageLevels,
                        CounterBitWidth => DVFSCounterResolution,
                        BaseNoCPos => RouterAddress(i, NoCXSize),
                        IsNoC => True
                    )

                    port map(

                        Clock => Clocks(i),
                        Reset => Reset,

                        ClockToCommStruct => RouterClocks(i),

                        SupplySwitchesEnable => DVFSRouterSwitchEnables(i),

                        LocalPortData => LocalPortInputs(i).DataOut,
                        LocalPortTX => LocalPortInputs(i).Tx,
                        LocalPortCreditI => LocalPortOutputs(i).CreditI,
                        LocalPortClockTX => LocalPortInputs(i).ClockTX

                    );

            end generate NoCDVFSControllers;

        end generate DVFSCond;

        -- Directly sets router clocks as entity interface given clocks (no DVFS)
        NODVFS: if not DVFSEnable generate
        
            RouterClocks <= Clocks;

        end generate NODVFS;
    
        -- Instantiates NoC
        NoCGen: entity work.Hermes

            generic map(
                NoCXSize => NoCXSize,
                NoCYSize => NoCYSize
            )
            port map(
                --Clocks => Clocks,
                Clocks => RouterClocks,
                Reset => Reset,
                PEInputs => LocalPortOutputs,
                PEOutputs => LocalPortInputs
            );
    
    end generate NoCCond;
    
    
    -- Instantiate Buses, if any are to be instantiated
    BusesCond: if AmountOfBuses > 0 generate

        -- Bus Parameters (from JSON config) 
        --  (These parameters must be conditially obtained here, instead of unconditionally in top-level declarative region along with the other Bus parameters, 
        -- because they are only exported to JSON in PlatformComposer if there is at least one Bus in the network topology, and so, must only be read from JSON if there is at least one Bus instantiated here in VHDL)
        constant AmountOfPEsInBuses: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInBuses");
        constant BusWrapperIDs: integer_vector(0 to AmountOfBuses - 1) := jsonGetIntegerArray(PlatCFG, "BusWrapperIDs");

        subtype BusPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestBus);  -- PEs + wrapper
        type BusPEAddresses_vector is array(natural range <>) of BusPEAddresses_t;
        
        function GetBusPEAddresses(PEInfo: PEInfo_vector; AmountOfBuses: integer; AmountOfPEsInBuses: integer_vector) return BusPEAddresses_vector is
            variable BusPEAddresses: BusPEAddresses_vector(0 to AmountOfBuses - 1);
        begin

            for i in 0 to AmountOfBuses - 1 loop
                BusPEAddresses(i)(0 to AmountOfPEsInBuses(i)) := GetPEAddresses(PlatCFG, PEInfo, "BUS", i);
            end loop;
            
            return BusPEAddresses;
        
        end function GetBusPEAddresses;
        
        constant BusPEAddresses: BusPEAddresses_vector(0 to AmountOfBuses - 1) := GetBusPEAddresses(PEInfo, AmountOfBuses, AmountOfPEsInBuses);

    begin

        -- Instantiates a DVFS controller for every Bus
        DVFSCond: if DVFSEnable generate

            BusDVFSControllers: for i in 0 to AmountOfBuses - 1 generate

                DVFSController: entity work.DVFSController

                    generic map(
                        DVFSServiceCode => DVFSServiceID,
                        AmountOfVoltageLevels => DVFSAmountOfVoltageLevels,
                        CounterBitWidth => DVFSCounterResolution,
                        BaseNoCPos => RouterAddress(BusWrapperIDs(i), NoCXSize),
                        IsNoC => False
                    )

                    port map(

                        Clock => Clocks(BusWrapperIDs(i)),
                        Reset => Reset,

                        ClockToCommStruct => BusClocks(i),

                        SupplySwitchesEnable => DVFSBusSwitchEnables(i),

                        LocalPortData => LocalPortInputs(BusWrapperIDs(i)).DataOut,
                        LocalPortTX => LocalPortInputs(BusWrapperIDs(i)).Tx,
                        LocalPortCreditI => LocalPortOutputs(BusWrapperIDs(i)).CreditI,
                        LocalPortClockTX => LocalPortInputs(BusWrapperIDs(i)).ClockTX

                    );

            end generate BusDVFSControllers;

        end generate DVFSCond;

        -- Set Bus clocks as same clocks of its associated Router, as given through entity interface (no DVFS)
        NODVFS: if not DVFSEnable generate

            SetBusClocks: for i in 0 to AmountOfBuses - 1 generate
                BusClocks(i) <= Clocks(BusWrapperIDs(i));
            end generate SetBusClocks;

        end generate NODVFS;

        -- Instantiates every Bus
        BusesGen: for i in 0 to AmountOfBuses - 1 generate 
        
            BusInstance: entity work.HyBus

                generic map(
                    Arbiter          => "RR",
                    --AmountOfPEs           => (AmountOfPEsInBuses(i) + 1),  -- TODO: Not add +1 if standalone
                    AmountOfPEs      => (AmountOfPEsInBuses(i) + CONV_INTEGER(not IsStandaloneBus)),
                    PEAddresses      => BusPEAddresses(i)(0 to AmountOfPEsInBuses(i)),
                    BridgeBufferSize => BridgeBufferSize,
                    IsStandalone     => IsStandaloneBus
                )
                port map(
                    --Clock     => Clocks(BusWrapperIDs(i)),  -- Clock of its wrapper
                    Clock     => BusClocks(i),
                    Reset     => Reset,  -- Global reset, from entity interface
                    PEInputs  => BusOutputInterfaces(i)(0 to AmountOfPEsInBuses(i)),
                    PEOutputs => BusInputInterfaces(i)(0 to AmountOfPEsInBuses(i))
                );

            assert false report "Instantiated Bus <" & integer'image(i) & "> with <" & integer'image(AmountOfPEsInBuses(i) + CONV_INTEGER(not IsStandaloneBus)) & "> elements" severity note;

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

        -- Crossbar Parameters (from JSON config) 
        --  (These parameters must be conditially obtained here, instead of unconditionally in top-level declarative region along with the other Crossbar parameters, 
        -- because they are only exported to JSON in PlatformComposer if there is at least one Crossbar in the network topology, and so, must only be read from JSON if there is at least one Crossbar instantiated here in VHDL)
        constant AmountOfPEsInCrossbars: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "AmountOfPEsInCrossbars");
        constant CrossbarWrapperIDs: integer_vector(0 to AmountOfCrossbars - 1) := jsonGetIntegerArray(PlatCFG, "CrossbarWrapperIDs");

        subtype CrossbarPEAddresses_t is HalfDataWidth_vector(0 to SizeOfLargestCrossbar);  -- PEs + wrapper
        type CrossbarPEAddresses_vector is array(natural range <>) of CrossbarPEAddresses_t;
        
        function GetCrossbarPEAddresses(PEInfo: PEInfo_vector; AmountOfCrossbars: integer; AmountOfPEsInCrossbars: integer_vector) return CrossbarPEAddresses_vector is
            variable CrossbarPEAddresses: CrossbarPEAddresses_vector(0 to AmountOfCrossbars - 1);
        begin
        
            for i in 0 to AmountOfCrossbars - 1 loop
                CrossbarPEAddresses(i)(0 to AmountOfPEsInCrossbars(i)) := GetPEAddresses(PlatCFG, PEInfo, "XBR", i);
            end loop;
            
            return CrossbarPEAddresses;
        
        end function GetCrossbarPEAddresses;
        
        constant CrossbarPEAddresses: CrossbarPEAddresses_vector(0 to AmountOfCrossbars - 1) := GetCrossbarPEAddresses(PEInfo, AmountOfCrossbars, AmountOfPEsInCrossbars);

    begin

        DVFSCond: if DVFSEnable generate

            CrossbarDVFSControllers: for i in 0 to AmountOfCrossbars - 1 generate

                DVFSController: entity work.DVFSController

                    generic map(
                        DVFSServiceCode => DVFSServiceID,
                        AmountOfVoltageLevels => DVFSAmountOfVoltageLevels,
                        CounterBitWidth => DVFSCounterResolution,
                        BaseNoCPos => RouterAddress(CrossbarWrapperIDs(i), NoCXSize),
                        IsNoC => False
                    )

                    port map(

                        Clock => Clocks(CrossbarWrapperIDs(i)),
                        Reset => Reset,

                        ClockToCommStruct => CrossbarClocks(i),

                        SupplySwitchesEnable => DVFSCrossbarSwitchEnables(i),

                        LocalPortData => LocalPortInputs(CrossbarWrapperIDs(i)).DataOut,
                        LocalPortTX => LocalPortInputs(CrossbarWrapperIDs(i)).Tx,
                        LocalPortCreditI => LocalPortOutputs(CrossbarWrapperIDs(i)).CreditI,
                        LocalPortClockTX => LocalPortInputs(CrossbarWrapperIDs(i)).ClockTX

                    );

            end generate CrossbarDVFSControllers;

        end generate DVFSCond;

        -- Set Bus clocks as same clocks of its associated Router, as given through entity interface (no DVFS)
        NODVFS: if not DVFSEnable generate

            SetCrossbarClocks: for i in 0 to AmountOfCrossbars - 1 generate
                CrossbarClocks(i) <= Clocks(CrossbarWrapperIDs(i));
            end generate SetCrossbarClocks;

        end generate NODVFS;

        CrossbarsGen: for i in 0 to AmountOfCrossbars - 1 generate

            -- Instantiate Crossbar
            CrossbarInstance: entity work.Crossbar

                generic map(
                    ArbiterType       => "RR",
                    --AmountOfPEs           => (AmountOfPEsInCrossbars(i) + 1),  -- TODO: Not add +1 if standalone
                    AmountOfPEs       => (AmountOfPEsInCrossbars(i) + CONV_INTEGER(not IsStandaloneCrossbar)),
                    PEAddresses       => CrossbarPEAddresses(i)(0 to AmountOfPEsInCrossbars(i)),
                    BridgeBufferSize  => BridgeBufferSize,
                    IsStandalone      => IsStandaloneCrossbar
                )
                port map(
                    --Clock     => Clocks(CrossbarWrapperIDs(i)),  -- Clock of its wrapper
                    Clock     => CrossbarClocks(i),
                    Reset     => Reset,  -- Global reset, from entity interface
                    PEInputs  => CrossbarOutputInterfaces(i)(0 to AmountOfPEsInCrossbars(i)),
                    PEOutputs => CrossbarInputInterfaces(i)(0 to AmountOfPEsInCrossbars(i))
                );
            
            assert false report "Instantiated Crossbar <" & integer'image(i) & "> with <" & integer'image(AmountOfPEsInCrossbars(i) + CONV_INTEGER(not IsStandaloneCrossbar)) & "> elements" severity note;

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


    -- Connects PE interfaces passed from top entity interface to local port of routers and into Bus-Crossbars
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
