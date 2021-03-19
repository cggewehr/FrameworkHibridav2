--------------------------------------------------------------------------------
-- Title       : Bus
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

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all; 


entity HyBus is

	generic(
		Arbiter: string := "RR";
		AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector;  -- As XY coordinates
		BridgeBufferSize: integer;
		IsStandalone: boolean := True
	);
	port(
		Clock: in std_logic;
		Reset: in std_logic;
		--PEInterfaces: inout PEInterface_vector
		PEInputs: out PEInputs_vector(0 to AmountOfPEs - 1);
		PEOutputs: in PEOutputs_vector(0 to AmountOfPEs - 1)
	);

end entity HyBus;


architecture RTL of HyBus is

	-- Set PEAddresses
	constant PEAddresses: HalfDataWidth_vector := SetPEAddresses(PEAddressesFromTop, UseDefaultPEAddresses, AmountOfPEs);

	-- Arbiter signals
	signal arbiterACK: std_logic;
	signal arbiterGrant: std_logic_vector(0 to AmountOfPEs - 1);
	signal arbiterRequest: std_logic_vector(0 to AmountOfPEs - 1);

	-- Bus signals
	signal busData: DataWidth_t;
	signal busTx: std_logic;
	signal busCredit: std_logic;

	-- Bus control signals
	signal controlRx: std_logic_vector(0 to AmountOfPEs - 1);
	signal controlCredit: std_logic_vector(0 to AmountOfPEs - 1);

begin

	-- Instantiates bridges
	BusBridgeGen: for i in 0 to AmountOfPEs - 1 generate

		BusBridge: entity work.BusBridge

			generic map(
				BufferSize => BridgeBufferSize
			)
			port map(

				-- Basic
				Clock   => Clock,
				Reset   => Reset,

				-- PE interface (Bridge input)
				ClockRx => PEOutputs(i).ClockTx,
				Rx      => PEOutputs(i).Tx,
				DataIn  => PEOutputs(i).DataOut,
				CreditO => PEInputs(i).CreditI,

				-- Bus interface (Bridge output)
				ClockTx => open,
				Tx      => busTx,
				DataOut => busData,
				CreditI => busCredit,

				-- Arbiter interface
				Ack     => arbiterACK,
				Request => arbiterRequest(i),
				Grant   => arbiterGrant(i)

			);

	end generate BusBridgeGen;
	

	-- Controls Rx of PEs based on what PE is currently using the bus
	BusControl: entity work.BusControl

		generic map(
			AmountOfPEs => AmountOfPEs,
			PEAddresses => PEAddresses
		)
		port map(

			-- Basic
			Clock => Clock,
			Reset => Reset,

			-- Bus interface
			BusData => busData,
			BusTx => busTx,
			BusCredit => busCredit,

			-- PE interface
			PERx => controlRx,
			PECredit => controlCredit

		);


	-- Instantiates Round Robin arbiter
	RoundRobinArbiterGen: if Arbiter = "RR" generate

		RoundRobinArbiter: entity work.BusRRArbiter

			generic map(
				AmountOfPEs => AmountOfPEs
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


	-- Connects PE input interfaces to bus 
	PEConnectGen: for i in 0 to AmountOfPEs - 1 generate
	
		PEInputs(i).DataIn <= busData;
		PEInputs(i).ClockRx <= Clock;
		PEInputs(i).Rx <= controlRx(i);
		controlCredit(i) <= PEOutputs(i).CreditO;
		
	end generate PEConnectGen;

end architecture RTL;
