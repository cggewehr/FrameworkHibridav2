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

	-- Arbiter interface signals
	signal arbiterACK: std_logic;
	signal arbiterGrant: std_logic_vector(0 to AmountOfPEs - 1);
	signal arbiterRequest: std_logic_vector(0 to AmountOfPEs - 1);

    -- Bridge interface signals
    signal bridgeDataOut: DataWidth_vector(0 to AmountOfPEs - 1);
    signal bridgeTx: std_logic_vector(0 to AmountOfPEs - 1);
    signal bridgeCreditI: std_logic_vector(0 to AmountOfPEs - 1);
    signal bridgeACK: std_logic_vector(0 to AmountOfPEs - 1);

	-- Bus data link signals
	signal busData: DataWidth_t;
	signal busTx: std_logic;
	signal busCredit: std_logic;

	-- Control signals
	signal RXEnable: std_logic_vector(0 to AmountOfPEs - 1);

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
				Tx      => bridgeTx(i),
				DataOut => bridgeDataOut(i),
				CreditI => bridgeCreditI(i),
				--CreditI => busCredit,

				-- Arbiter interface
				Ack     => bridgeACK(i),
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

            -- Arbiter interface
            ACK => arbiterACK,

			-- PE interface
            RXEnable => RXEnable

		);

	-- Instantiates arbiter as given by "Arbiter" generic
	ArbiterFactory: entity work.ArbiterFactory

			generic map(
				ArbiterType => Arbiter,
				AmountOfPEs => AmountOfPEs
			)

			port map(
				
				Clock => Clock,
				Reset => Reset,

                ACK   => arbiterACK,
                Grant => arbiterGrant,
                Req   => arbiterRequest

			);

	-- Connects PE input interfaces to bus 
	LinkGen: for i in 0 to AmountOfPEs - 1 generate

        busData <= bridgeDataOut(i) when arbiterGrant(i) = '1' else (others => 'Z'); 
        busTx <= bridgeTx(i) when arbiterGrant(i) = '1' else 'Z';  
        arbiterACK <= bridgeACK(i) when arbiterGrant(i) = '1' else 'Z';
        bridgeCreditI(i) <= busCredit when arbiterGrant(i) = '1' else '0';
	
		PEInputs(i).DataIn <= busData;
		PEInputs(i).ClockRx <= Clock;
		PEInputs(i).Rx <= busTx when RXEnable(i) = '1' else '0';
		busCredit <= PEOutputs(i).CreditO when RXEnable(i) = '1' else 'Z';
		
	end generate LinkGen;

end architecture RTL;
