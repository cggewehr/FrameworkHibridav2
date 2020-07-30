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
-- TODO        :
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.std_logic_unsigned.all;
    use ieee.numeric_std.all;

library work;
    use work.HyHeMPS_PKG.all;
    use work.JSON.all;


entity PE is 

    generic(
        -- Path to JSON file containing PE and APP parameters
        PEConfigFile        : string := "PESample.json";
        InjectorConfigFile  : string := "InjectorSample.json";
        PlatformConfigFile  : string := "PlatformSample.json";
        InboundLogFilename  : string;
        OutboundLogFilename : string
    );

    port(

        -- Basic
	    --Clock   : in  std_logic;
        Reset   : in  std_logic;

	      -- Output Interface (Injector)
        ClockTx : out std_logic;
        Tx      : out std_logic;
        DataOut : out DataWidth_t;
        CreditI : in  std_logic;

        -- Input Interface (Receiver)
        ClockRx : in  std_logic;        
        Rx      : in  std_logic;
        DataIn  : in  DataWidth_t;
        CreditO : out std_logic

    );

end entity PE;


architecture Injector of PE is

    -- JSON config files
    constant PEJSONConfig: T_JSON := jsonLoad(PEConfigFile);

    -- Injector parameters ("FXD", "DPD")
    constant InjectorType: string(1 to 3) := jsonGetString(PEJSONConfig, "InjectorType");
    constant InjectorClockPeriod: real := jsonGetReal(PEJSONConfig, "InjectorClockPeriod"); -- in ns
    signal injectorClock: std_logic := '0';

    -- Buffer signals
    constant BufferSize: integer := jsonGetInteger(PEJSONConfig, "OutBufferSize");
    signal bufferDataIn: DataWidth_t;
    signal bufferRx: std_logic;
    signal bufferAVFlag: std_logic;

begin 

  	ClockTx <= injectorClock;


  	-- Generates clock from clock period defined in JSON config
  	InjectorClockGenerator: process begin

    	injectorClock <= '0';
        wait for (InjectorClockPeriod / 2.0) * 1 ns;
        injectorClock <= '1';
        wait for (InjectorClockPeriod / 2.0) * 1 ns;

    end process InjectorClockGenerator;


    -- Instantiates a message injector, which produces and logs messages and insert them in the output buffer
    Injector: entity work.Injector

        generic map(
            PEConfigFile => PEConfigFile,
            InjectorConfigFile => InjectorConfigFile,
            PlatformConfigFile => PlatformConfigFile,
            OutboundLogFilename => OutboundLogFilename
        )
        port map(

            -- Basic
            Clock => injectorClock,
            Reset => Reset,

            -- Output Interface
            DataOut => bufferDataIn,
            DataOutAV => bufferRx,
            OutputBufferSlotAvailable => bufferAVFlag

        );


    -- Instantiates a receiver, which generate a log of all incoming messages
    Receiver: entity work.Receiver

      	generic map(
      		InboundLogFilename => InboundLogFilename
      	)
      	port map(

      		Clock   => ClockRx,
      		Reset   => Reset,
      		DataIn  => DataIn,
      		Rx      => Rx,
      		CreditO => CreditO

      	);


    -- Instantiates a buffer in which the Injector inserts flits
    OutBuffer: entity work.CircularBuffer 

        generic map(
            BufferSize => BufferSize,
            DataWidth  => DataWidth  -- from HyHeMPS_PKG
        )
        port map(
            
            -- Basic
            Reset               => Reset,

            -- PE Interface (Input)
            ClockIn             => injectorClock,
            DataIn              => bufferDataIn,
            DataInAV            => bufferRx,
            WriteACK            => open,

            -- Comm structure interface (Output)
            ClockOut            => injectorClock,
            DataOut             => DataOut,
            ReadConfirm         => CreditI,
            ReadACK             => open,
            
            -- Status flags
            BufferEmptyFlag     => open,
            BufferFullFlag      => open,
            BufferReadyFlag     => Tx,
            BufferAvailableFlag => bufferAVFlag

        );

end architecture Injector;


--architecture Plasma of PE is

--begin
    
--end architecture Plasma;
