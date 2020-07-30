--------------------------------------------------------------------------------
-- Title       : Crossbar
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : Crossbar.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Implements a Crossbar interconnect, in which PEs have a direct
--               connection to each another, but still must compete for access 
--               to targets input buffer.
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


entity Crossbar is

	generic(
		ArbiterType: string;
		AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector;  -- As XY coordinates
		BridgeBufferSize: integer;
		IsStandalone: boolean
	);
	port(
		Clock: in std_logic;
		Reset: in std_logic;
		PEInterfaces: inout PEInterface_vector
	);
	
end entity Crossbar;


architecture RTL of Crossbar is

	-- Bridge output interface
	signal bridgeTx: std_logic_vector(0 to AmountOfPEs - 1);
	signal bridgeDataOut: DataWidth_vector(0 to AmountOfPEs - 1);
	signal bridgeCredit: std_logic_vector(0 to AmountOfPEs - 1);

	-- Bridge to Arbiter interface
	signal bridgeACK: std_logic_vector(0 to AmountOfPEs - 1);
	signal bridgeRequest: std_logic_vector(0 to AmountOfPEs - 1);
	signal bridgeGrant: std_logic_vector(0 to AmountOfPEs - 1);

	-- CrossbarControl input interface
	subtype CtrlDataIn_t is DataWidth_vector(0 to AmountOfPEs - 1);
	type CtrlDataIn_vector is array(0 to AmountOfPEs - 1) of CtrlDataIn_t;
	signal controlDataIn: CtrlDataIn_vector;

	subtype slv_t is std_logic_vector(0 to AmountOfPEs - 1);
	type slv_vector is array(0 to AmountOfPEs - 1) of slv_t;
	signal controlRx: slv_vector;
	signal controlCreditO: slv_vector;

	-- Arbiter interface
	signal arbiterRequest: slv_vector;
	signal arbiterACK: slv_vector;
	signal arbiterGrant: slv_vector;
	signal arbiterNewGrant: std_logic_vector(0 to AmountOfPEs - 1);

begin

	-- Instantiates bridges
	CrossbarBridgeGen: for i in 0 to AmountOfPEs - 1 generate

		CrossbarBridge: entity work.CrossbarBridge

			generic map(
				BufferSize  => BridgeBufferSize,
				AmountOfPEs => AmountOfPEs,
				PEAddresses => PEAddresses,
				SelfAddress => PEAddresses(i)
			)

			port map(

				-- Basic
				Clock => Clock,
				Reset => Reset,

				-- PE interface (Bridge input)
				ClockRx => PEInterfaces(i).ClockRx,
				Rx      => PEInterfaces(i).Tx,
				DataIn  => PEInterfaces(i).DataOut,
				CreditO => PEInterfaces(i).CreditI,

				-- Crossbar interface (Bridge output)
				ClockTx => open,
				Tx      => bridgeTx(i),
				DataOut => bridgeDataOut(i),
				CreditI => bridgeCredit,

				-- Arbiter interface
				Ack     => bridgeACK,
				Request => bridgeRequest,
				Grant   => bridgeGrant

			);

	end generate CrossbarBridgeGen;


	-- Instantiates input controllers
	CrossbarControlGen: for i in 0 to AmountOfPEs - 1 generate

		CrossbarControl: entity work.CrossbarControl

			generic map(
				PEAddresses => PEAddresses,
				SelfAddress => PEAddresses(i),
				IsStandalone => IsStandalone
			)
			port map(
				
				-- Basic
				Clock => Clock,
				Reset => Reset,

				-- Input interface (Crossbar)
				DataInMux => controlDataIn(i),
				RxMux     => controlRx(i),
				CreditO   => controlCreditO(i),

				-- Output interface (PE input)
				PEDataIn  => PEInterfaces(i).DataIn,
				PERx      => PEInterfaces(i).Rx,
				PECreditO => PEInterfaces(i).CreditO,
				
				-- Arbiter interface
				NewGrant  => arbiterNewGrant(i)

			);

			ControlConnectGen: for j in 0 to AmountOfPEs - 1 generate

				ControlMap: if i /= j generate

					controlDataIn(i)(j) <= bridgeDataOut(j);
					controlRx(i)(j) <= bridgeTx(j);
					bridgeCredit(i) <= controlCreditO(i)(j);

				end generate ControlMap;

				ControlGround: if i = j generate

					controlDataIn(i)(j) <= (others => '0');
					controlRx(i)(j) <= '0';
					bridgeCredit(i) <= '0';

				end generate ControlGround;

			end generate ControlConnectGen;

	end generate CrossbarControlGen;


	-- Instantiates arbiters as given by "Arbiter" generic
	ArbiterGen: for Arbiter in 0 to AmountOfPEs - 1 generate

		RoundRobinArbiterGen: if ArbiterType = "RR" generate

			RoundRobinArbiter: entity work.CrossbarRRArbiter

				generic map(
					AmountOfPEs => AmountOfPEs
				)
				port map(
					Clock => Clock,
					Reset => Reset,
					Ack   => arbiterACK(Arbiter),
					Grant => arbiterGrant(Arbiter),
					Req   => arbiterRequest(Arbiter),
					NewGrant => arbiterNewGrant(Arbiter)
				);

		end generate RoundRobinArbiterGen;
		
--		DaisyChainArbiterGen: if ArbiterType = "DC" generate
		
--            DaisyChainArbiter: entity work.CrossbarDCArbiter

--				generic map(
--					AmountOfPEs => AmountOfPEs
--				)
--				port map(
--					Clock => Clock,
--					Reset => Reset,
--					Ack   => arbiterACK(Arbiter),
--					Grant => arbiterGrant(Arbiter),
--					Req   => arbiterRequest(Arbiter)
--				);
		
--		end generate DaisyChainArbiterGen;

		ArbConnectGen: for Bridge in 0 to AmountOfPEs - 1 generate

			ArbMap: if Bridge /= Arbiter generate

				arbiterACK(Arbiter)(Bridge) <= bridgeACK(Bridge);
				arbiterGrant(Arbiter)(Bridge) <= bridgeGrant(Bridge);
				bridgeRequest(Bridge) <= arbiterRequest(Arbiter)(Bridge);

			end generate ArbMap;

			ArbGround: if Bridge = Arbiter generate

				arbiterACK(Arbiter)(Bridge) <= '0';
				arbiterGrant(Arbiter)(Bridge) <= '0';
				bridgeRequest(Bridge) <= '0';

			end generate ArbGround;

		end generate ArbConnectGen;

	end generate ArbiterGen;

end architecture RTL;
