--------------------------------------------------------------------------------
-- Title       : PEBus
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : Bus.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Implements a Bus interconnect, in which PEs compete for access
--               to a shared communication medium.
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : 
--------------------------------------------------------------------------------

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;
	use work.Injector_PKG.all;


entity PEBus is

	generic(
		Arbiter: string;
		AmountOfInjectors: integer;
		BridgeBufferSize: integer
	);
	port(

		-- Basic
		Clock: in std_logic;
		Reset: in std_logic;

		-- Input Interface (from Injectors)
		InjectorInterfaces: inout InjectorInterface_vector;

		-- Output Interface (to comm structure)
		DataOut: out DataWidth_t;
		DataOutAV: out std_logic;
		CreditI: in std_logic;
		ClockTx: out std_logic
	);

end entity PEBus;


architecture RTL of PEBus is

	-- Arbiter signals
	signal arbiterACK: std_logic;
	signal arbiterGrant: std_logic_vector(0 to AmountOfInjectors - 1);
	signal arbiterRequest: std_logic_vector(0 to AmountOfInjectors - 1);

	-- Bus signals
	signal busData: DataWidth_t;
	signal busTx: std_logic;
	--signal busCredit: std_logic;

	-- Bus control signals
	--signal controlRx: std_logic_vector(0 to AmountOfPEs - 1);
	--signal controlCredit: std_logic_vector(0 to AmountOfPEs - 1);

begin

	-- Instantiates bridges
	BusBridgeGen: for i in 0 to AmountOfInjectors - 1 generate

		BusBridge: entity work.BusBridge

			generic map(
				BufferSize => BridgeBufferSize
			)
			port map(

				-- Basic
				Clock   => Clock,
				Reset   => Reset,

				-- Input interface (from Injectors)
				ClockRx => InjectorInterfaces(i).Clock,
				Rx      => InjectorInterfaces(i).DataOutAV,
				DataIn  => InjectorInterfaces(i).DataOut,
				CreditO => InjectorInterfaces(i).OutputBufferAvailableFlag,

				-- Output interface (to comm structure)
				ClockTx => open,
				Tx      => BusTx,
				DataOut => BusData,
				CreditI => CreditI,

				-- Arbiter interface
				Ack     => arbiterACK,
				Request => arbiterRequest(i),
				Grant   => arbiterGrant(i)

			);

	end generate BusBridgeGen;
	

	-- Controls Rx of PEs based on what PE is currently using the bus
	--BusControl: entity work.BusControl

	--	generic map(
	--		AmountOfPEs => AmountOfPEs,
	--		PEAddresses => PEAddresses
	--	)
	--	port map(

	--		-- Basic
	--		Clock => Clock,
	--		Reset => Reset,

	--		-- Bus interface
	--		BusData => busData,
	--		BusTx => busTx,
	--		BusCredit => busCredit,

	--		-- PE interface
	--		PERx => controlRx,
	--		PECredit => controlCredit

	--	);

	-- Instantiates Round Robin arbiter
	RoundRobinArbiterGen: if Arbiter = "RR" generate

		RoundRobinArbiter: entity work.BusRRArbiter

			generic map(
				AmountOfPEs => AmountOfInjectors
			)
			port map (
				Clock => Clock,
				Reset => Reset,
				Ack   => arbiterACK,
				Grant => arbiterGrant,
				Req   => arbiterRequest
			);

	end generate RoundRobinArbiterGen;

 
	-- Instantiates Daisy Chain arbiter
	--DaisyChainArbiterGen: if Arbiter = "DC" generate

	--	DaisyChainArbiter: entity work.DaisyChainArbiter

	--		generic map(
	--			AmountOfPEs => AmountOfPEs
	--		)
	--		port map (
	--			Clock   => Clock,
	--			Reset   => Reset,
	--			Ack     => arbiterACK,
	--			Grant   => arbiterGrant,
	--			Request => arbiterRequest
	--		);

	--end generate DaisyChainArbiterGen;


	-- Connects PE interfaces to bus 
	INJConnectGen: for i in 0 to AmountOfInjectors - 1 generate
	
		busData <= InjectorInterfaces(i).DataOut;  -- Tristated @ bridge
		busTx <= InjectorInterfaces(i).DataOutAV;  -- Tristated @ bridge
		InjectorInterfaces(i).OutputBufferAvailableFlag <= CreditI;
		
	end generate INJConnectGen;

	-- Connects Bus to comm structure
	DataOut <= busData when Reset = '0' else (others => '0');
	DataOutAV <= busTx when Reset = '0' else '0';
	ClockTx <= Clock; 

end architecture RTL;
