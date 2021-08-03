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
	signal bridgeRequest: std_logic_vector(0 to AmountOfPEs - 1);

	-- Bus data link signals
	signal busData: DataWidth_t;
	signal busTx: std_logic;
	signal busCredit: std_logic;

	-- Control signals
	signal RXEnable: std_logic_vector(0 to AmountOfPEs - 1);
	signal TXEnable: std_logic_vector(0 to AmountOfPEs - 1);
	signal requestFromNoC: std_logic;
	signal interrupted: std_logic;

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
				--Request => arbiterRequest(i),
				Request => bridgeRequest(i),
				--Grant   => arbiterGrant(i)
				Grant   => TXEnable(i)

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

			-- NoC interrupt handler
			RequestFromNoC => requestFromNoC,  -- Set to 0 if standalone
			Interrupted => interrupted,  -- Unused if standalone

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

	StandaloneGen: if IsStandalone generate
		RequestFromNoC <= '0';
	end generate;


	NoCGen: if not IsStandalone generate
		RequestFromNoC <= arbiterRequest(AmountOfPEs - 1);
	end generate;

	-- 
	RequestGen: for i in 0 to AmountOfPEs - 1 generate

		StandaloneRequestGen: if IsStandalone generate
			arbiterRequest(i) <= bridgeRequest(i);
		end generate StandaloneRequestGen;

		HybridRequestGen: if not IsStandalone generate

			PERequestGen: if i /= AmountOfPEs - 1 generate
				arbiterRequest(i) <= '1' when bridgeRequest(i) = '1' and arbiterRequest(AmountOfPEs - 1) = '0' else '0'; 
			end generate PERequestGen;

			NoCRequestGen: if i = AmountOfPEs - 1 generate
				arbiterRequest(i) <= bridgeRequest(i);
			end generate NoCRequestGen;

		end generate HybridRequestGen;

	end generate RequestGen;

	--
	EnableGen: for i in 0 to AmountOfPEs - 1 generate

		StandaloneEnableGen: if IsStandalone generate
			TXEnable(i) <= arbiterGrant(i);
		end generate StandaloneEnableGen;

		HybridEnableGen: if not IsStandalone generate

			PEEnableGen: if i /= AmountOfPEs - 1 generate
				TXEnable(i) <= '1' when arbiterGrant(i) = '1' and interrupted = '0' else '0';
			end generate PEEnableGen;

			NoCEnableGen: if i = AmountOfPEs - 1 generate
				TXEnable(i) <= '1' when arbiterGrant(i) = '1' or interrupted = '1' else '0';
			end generate NoCEnableGen;

		end generate HybridEnableGen;

	end generate EnableGen;


	-- Connects PE input interfaces to bus 
	LinkGen: for i in 0 to AmountOfPEs - 1 generate

        busData <= bridgeDataOut(i) when TXEnable(i) = '1' else (others => 'Z'); 
        busTx <= bridgeTx(i) when TXEnable(i) = '1' else 'Z';  
        arbiterACK <= bridgeACK(i) when TXEnable(i) = '1' else 'Z';
        bridgeCreditI(i) <= busCredit when TXEnable(i) = '1' else '0';
	
		PEInputs(i).DataIn <= busData;
		PEInputs(i).ClockRx <= Clock;
		PEInputs(i).Rx <= busTx when RXEnable(i) = '1' else '0';
		busCredit <= PEOutputs(i).CreditO when RXEnable(i) = '1' else 'Z';
		
	end generate LinkGen;

end architecture RTL;
