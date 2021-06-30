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

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;
    use HyHeMPS.Injector_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;
    --use work.Injector_PKG.all;


entity PEBus is

	generic(
		Arbiter: string;
		AmountOfInjectors: integer;
		BridgeBufferSize: integer;
		PEPos: integer
	);
	port(

		-- Basic
		Clock: in std_logic;
		Reset: in std_logic;

		-- Input Interfaces (from Injectors)
		--InjectorInterfaces: inout InjectorInterface_vector;
        ClockRx: in std_logic_vector(0 to AmountOfInjectors - 1);
        Rx: in std_logic_vector(0 to AmountOfInjectors - 1);
        DataIn: in DataWidth_vector(0 to AmountOfInjectors - 1);
        CreditO: out std_logic_vector(0 to AmountOfInjectors - 1);

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
	InjBufferGen: for i in 0 to AmountOfInjectors - 1 generate

		--BusBridge: entity work.BusBridge
		InjBuffer: entity work.InjBuffer

			generic map(
				BufferSize => BridgeBufferSize,
				PEPos => PEPos
			)
			port map(

				-- Basic
				Clock   => Clock,
				Reset   => Reset,

				-- Input interface (from Injectors)
				--ClockRx => InjectorInterfaces(i).Clock,
                ClockRx => ClockRx(i),
				--Rx      => InjectorInterfaces(i).DataOutAV,
				Rx      => Rx(i),
				--DataIn  => InjectorInterfaces(i).DataOut,
				DataIn  => DataIn(i),
				--CreditO => InjectorInterfaces(i).OutputBufferAvailableFlag,
				CreditO => CreditO(i),

				-- Output interface (to comm structure)
				ClockTx => open,
				Tx      => busTx,
				DataOut => busData,
				CreditI => CreditI,

				-- Arbiter interface
				Ack     => arbiterACK,
				Request => arbiterRequest(i),
				Grant   => arbiterGrant(i)

			);

	end generate InjBufferGen;
	

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

	-- Instantiates arbiter
	RoundRobinArbiter: entity work.ArbiterFactory

		generic map(
			AmountOfPEs => AmountOfInjectors,
            ArbiterType => Arbiter
		)
		port map (
			Clock => Clock,
			Reset => Reset,
			Ack   => arbiterACK,
			Grant => arbiterGrant,
			Req   => arbiterRequest
		);

 
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
	--INJConnectGen: for i in 0 to AmountOfInjectors - 1 generate
	
		--busData <= InjectorInterfaces(i).DataOut;  -- Tristated @ bridge
		--busTx <= InjectorInterfaces(i).DataOutAV;  -- Tristated @ bridge
		--InjectorInterfaces(i).OutputBufferAvailableFlag <= CreditI;
		
	--end generate INJConnectGen;

	-- Connects Bus to comm structure
	DataOut <= busData when Reset = '0' else (others => '0');
	DataOutAV <= busTx when Reset = '0' else '0';
	ClockTx <= Clock; 

end architecture RTL;
