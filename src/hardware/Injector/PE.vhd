--------------------------------------------------------------------------------
-- Title       : PE
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : PE.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Container for a single msg injector and receiver
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--             : v1.0 - Verified
--------------------------------------------------------------------------------
-- TODO        : Make NI
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;
    use HyHeMPS.Injector_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;
    --use work.Injector_PKG.all;
    --use work.JSON.all;


entity PE is 

    generic(
        -- Path to JSON file containing PE and APP parameters
        PEConfigFile       : string;
        PlatformConfigFile : string;
        ConfigPath         : string := "./flow/";
        LogPath            : string := "./log/"
    );

    port(

        -- Basic
	    --Clock   : in  std_logic;
        Reset   : in  std_logic;

	    -- Output Interface (from Injectors, through PEBus)
        ClockTx : out std_logic;
        Tx      : out std_logic;
        DataOut : out DataWidth_t;
        CreditI : in  std_logic;

        -- Input Interface (to Receiver)
        ClockRx : in  std_logic;        
        Rx      : in  std_logic;
        DataIn  : in  DataWidth_t;
        CreditO : out std_logic

    );

end entity PE;


architecture Injector of PE is

    -- JSON config files
    constant PEJSONConfig: T_JSON := jsonLoad(PEConfigFile);
    constant PlatCFG: T_JSON := jsonLoad(PlatformConfigFile);

    constant PEPos: integer := jsonGetInteger(PEJSONConfig, "PEPos");
    constant SquareNoCBound: integer := jsonGetInteger(PlatCFG, "SquareNoCBound");
    constant BusArbiter: string(1 to 2) := jsonGetString(PEJSONConfig, "BusArbiter");
    constant BusBridgeBufferSize: integer := jsonGetInteger(PEJSONConfig, "BridgeBufferSize");

    --
    constant AmountOfThreads: integer := jsonGetInteger(PEJSONConfig, "AmountOfThreads");
    constant AmountOfFlows: integer := jsonGetInteger(PEJSONConfig, "AmountOfFlows");
    constant MaxAmountOfFlows: integer := jsonGetInteger(PEJSONConfig, "LargestAmountOfFlows");
    constant AmountOfFlowsInThread: integer_vector(0 to AmountOfThreads - 1) := jsonGetIntegerArray(PEJSONConfig, "AmountOfFlowsInThread");

    constant ThreadID: integer_vector(0 to AmountOfThreads - 1) := jsonGetIntegerArray(PEJSONConfig, "ThreadID");
    constant AppID: integer_vector(0 to AmountOfThreads - 1) := jsonGetIntegerArray(PEJSONConfig, "AppID");

    -- Injector/Trigger signals
    type InjectorInterface_2vector is array(0 to AmountOfThreads - 1, 0 to MaxAmountOfFlows - 1) of InjectorInterface;
    signal InjectorInterfaces_2D: InjectorInterface_2vector;

    signal ClockRxBus: std_logic_vector(0 to AmountOfFlows - 1);
    signal RxBus: std_logic_vector(0 to AmountOfFlows - 1);
    signal DataInBus: DataWidth_vector(0 to AmountOfFlows - 1);
    signal CreditOBus: std_logic_vector(0 to AmountOfFlows - 1);

    -- Temp signals for output ports (used in Logger interface)
    signal txBuffer: std_logic;
    signal clockTxBuffer: std_logic;
    signal dataOutBuffer: DataWidth_t;
    signal creditOBuffer: std_logic;

    function get_i(ThreadNum: integer; FlowNum: integer; AmountOfFlowsInThread: integer_vector) return integer is 
        variable i: integer := 0;
    begin

        if ThreadNum = 0 then
            return FlowNum;
        end if;

        -- Sum amount of flows in previous threads (before thread of interest)
        SumPrevThreads: for Thread in 0 to ThreadNum - 1 loop
            i := i + AmountOfFlowsInThread(Thread);
        end loop SumPrevThreads;

        return i + FlowNum;

    end function get_i;

    --signal InjectorInterfaces_1D: InjectorInterface_vector(0 to AmountOfFlows - 1) := InjectorInterfaceTo1D(InjectorInterfaces_2D, AmountOfFlows);
    signal InjectorInterfaces_1D: InjectorInterface_vector(0 to AmountOfFlows - 1);

    
begin 

    -- Instantiates Injectors and Triggers
  	InjectorGenThread: for ThreadNum in 0 to AmountOfThreads - 1 generate

        InjectorGenFlow: for FlowNum in 0 to AmountOfFlowsInThread(ThreadNum) - 1 generate

            Injector: entity work.Injector

                generic map(
                    InjectorConfigFile => ConfigPath & "PE " & integer'image(PEPos) & "/Thread " & integer'image(ThreadNum) & "/Flow " & integer'image(FlowNum) & ".json",                 
                    PlatformConfigFile => PlatformConfigFile
                )
                port map(
                    Clock => InjectorInterfaces_2D(ThreadNum, FlowNum).Clock,
                    Reset => Reset,
                    Enable => InjectorInterfaces_2D(ThreadNum, FlowNum).Enable,
                    LastFlitFlag => InjectorInterfaces_2D(ThreadNum, FlowNum).LastFlitFlag,
                    DataOut => InjectorInterfaces_2D(ThreadNum, FlowNum).DataOut,
                    DataOutAV => InjectorInterfaces_2D(ThreadNum, FlowNum).DataOutAV,
                    OutputBufferAvailableFlag => InjectorInterfaces_2D(ThreadNum, FlowNum).OutputBufferAvailableFlag
                );

            Trigger: entity work.Trigger

                generic map(
                    InjectorConfigFile => ConfigPath & "PE " & integer'image(PEPos) & "/Thread " & integer'image(ThreadNum) & "/Flow " & integer'image(FlowNum) & ".json",
                    PlatformConfigFile => PlatformConfigFile
                )
                port map(
                    Reset => Reset,
                    Enable => InjectorInterfaces_2D(ThreadNum, FlowNum).Enable,
                    LastFlitFlag => InjectorInterfaces_2D(ThreadNum, FlowNum).LastFlitFlag,
                    InjectorClock => InjectorInterfaces_2D(ThreadNum, FlowNum).Clock,
                    OutputBufferAvailableFlag => InjectorInterfaces_2D(ThreadNum, FlowNum).OutputBufferAvailableFlag
                ); 

            -- Translates interface mapping from InjInterfaces2D[Thread][Flow] to InjInterfaces1D[i], where 0 < i < MaxAmountOfFlows
            MapTo1D: if AmountOfFlows > 1 generate

                --InjectorInterfaces_1D(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)).Clock <= InjectorInterfaces_2D(ThreadNum, FlowNum).Clock;
                --InjectorInterfaces_1D(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)).Enable <= InjectorInterfaces_2D(ThreadNum, FlowNum).Enable;
                --InjectorInterfaces_1D(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)).DataOut <= InjectorInterfaces_2D(ThreadNum, FlowNum).DataOut;
                --InjectorInterfaces_1D(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)).DataOutAV <= InjectorInterfaces_2D(ThreadNum, FlowNum).DataOutAV;
                --InjectorInterfaces_2D(ThreadNum, FlowNum).OutputBufferAvailableFlag <= InjectorInterfaces_1D(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)).OutputBufferAvailableFlag;

                ClockRxBus(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)) <= InjectorInterfaces_2D(ThreadNum, FlowNum).Clock;
                RxBus(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)) <= InjectorInterfaces_2D(ThreadNum, FlowNum).DataOutAV;
                DataInBus(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread)) <= InjectorInterfaces_2D(ThreadNum, FlowNum).DataOut;
                InjectorInterfaces_2D(ThreadNum, FlowNum).OutputBufferAvailableFlag <= CreditOBus(get_i(ThreadNum, FlowNum, AmountOfFlowsInThread));

            end generate MapTo1D;

        end generate InjectorGenFlow;

    end generate InjectorGenThread;

    -- Grounds outputs if no injectors are instantiated
    GroundGen: if AmountOfFlows = 0 generate

        --ClockTx <= ClockRx;
        --DataOut <= (others => '0');
        --Tx <= '0';
        clockTxBuffer <= ClockRx;
        dataOutBuffer <= (others => '0');
        txBuffer <= '0';
    
    end generate GroundGen;

    -- Directly connects buffer to PE output interface (no PEBus is necessary)
    DirectConnectGen: if AmountOfFlows = 1 generate

        InjBuffer: entity work.InjBuffer

            generic map(
                --BufferSize => BusBridgeBufferSize,
                BufferSize => 256,
                PEPos => PEPos
            )
            port map(
                
                Clock => ClockRx,
                Reset => Reset,

                -- Injector Interface
                --ClockRx => ClockRx,
                ClockRx => InjectorInterfaces_2D(0, 0).Clock,
                Rx => InjectorInterfaces_2D(0, 0).DataOutAV,
                DataIn => InjectorInterfaces_2D(0, 0).DataOut,
                CreditO => InjectorInterfaces_2D(0, 0).OutputBufferAvailableFlag,

                -- Struct Interface
                --ClockTx => ClockTx,
                ClockTx => clockTxBuffer,
                --Tx => Tx,
                Tx => txBuffer,
                --DataOut => DataOut,
                DataOut => dataOutBuffer,
                CreditI => CreditI,

                -- Arbiter Interface
                ACK => open,
                Request => open,
                Grant => '1'

            );

    end generate DirectConnectGen;


    PEBusGen: if AmountOfFlows > 1 generate

        PEBus: entity work.PEBus

            generic map(
                Arbiter => BusArbiter,
                AmountOfInjectors => AmountOfFlows,
                --BridgeBufferSize => BusBridgeBufferSize,
                BridgeBufferSize => 256,
                PEPos => PEPos
            ) 
            port map(

                -- Basic
                Clock => ClockRx,
                Reset => Reset,

                -- Input Interface (from Injectors)
                --InjectorInterfaces => InjectorInterfaces_1D,
                ClockRx => ClockRxBus,
                Rx => RxBus,
                DataIn => DataInBus,
                CreditO => CreditOBus,

                -- Output Interface (to comm structure)
                --DataOut => DataOut,
                DataOut => dataOutBuffer,
                --DataOutAV => Tx,
                DataOutAV => txBuffer,
                CreditI => CreditI,
                --ClockTx => ClockTx
                ClockTx => clockTxBuffer

            );

    end generate PEBusGen;


    -- Maps out signals in interface to temp signals
    ClockTx <= clockTxBuffer;
    Tx <= txBuffer;
    DataOut <= dataOutBuffer;
    creditOBuffer <= '1';
    CreditO <= creditOBuffer;


    -- Instantiates a receiver, which generates a log of all incoming messages
    Logger: entity work.Logger

      	generic map(
      		InboundLogFilename => LogPath & "PE " & integer'image(PEPos) & "/InLog" & integer'image(PEPos) & ".txt",
            OutboundLogFilename => LogPath & "PE " & integer'image(PEPos) & "/OutLog" & integer'image(PEPos) & ".txt",
      		SquareNoCBound => SquareNoCBound
      	)
      	port map(

                Reset => Reset,

                -- From network
                ClockRx => ClockRx,
                Rx => Rx,
                DataIn => DataIn,
                CreditO => creditOBuffer,

                -- To network
                ClockTx => clockTxBuffer,
                Tx => txBuffer,
                DataOut => dataOutBuffer,
                CreditI => CreditI

      	);

end architecture Injector;
