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
--               to target's input buffer.
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


entity Crossbar is

	generic(
		ArbiterType: string := "RR";
		AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector;  -- As XY coordinates
		BridgeBufferSize: integer;
		IsStandalone: boolean
	);
	port(

		Clock: in std_logic;
		Reset: in std_logic;

		PEInputs: out PEInputs_vector(0 to AmountOfPEs - 1);
		PEOutputs: in PEOutputs_vector(0 to AmountOfPEs - 1)

	);
	
end entity Crossbar;


architecture RTL of Crossbar is

	-- Arbiter interface
	subtype slv_t is std_logic_vector(0 to AmountOfPEs - 1);
	type slv_vector is array(0 to AmountOfPEs - 1) of slv_t;
	signal arbiterRequest: slv_vector;
	signal arbiterACK: std_logic_vector(0 to AmountOfPEs - 1);
	signal arbiterGrant: slv_vector;

    -- Bridge output interface
	signal bridgeTx: std_logic_vector(0 to AmountOfPEs - 1);
	signal bridgeDataOut: DataWidth_vector(0 to AmountOfPEs - 1);
	signal bridgeCreditI: std_logic_vector(0 to AmountOfPEs - 1);

	-- Bridge to Arbiter interface
	signal bridgeACK: std_logic_vector(0 to AmountOfPEs - 1);
	signal bridgeRequest: slv_vector;
	signal bridgeGrant: std_logic_vector(0 to AmountOfPEs - 1);

	-- Switch control signals
	signal switchEnable: std_logic_vector(0 to AmountOfPEs - 1);
	signal switchSelect: slv_vector;

    -- Performs "or" operation between all elements of a given std_logic_vector
	function OrReduce(inputArray: std_logic_vector) return std_logic is
		variable orReduced: std_logic := '0';
	begin

		for i in inputArray'range loop 

			orReduced := orReduced or inputArray(i);

		end loop;

		return orReduced;
		
	end function OrReduce;

begin

	-- Instantiates bridges
	CrossbarBridgeGen: for i in 0 to AmountOfPEs - 1 generate

        --PEInterfaces(i).ClockTx <= Clock;
        PEInputs(i).ClockRx <= Clock;

		CrossbarBridge: entity work.CrossbarBridge

			generic map(
				BufferSize  => BridgeBufferSize,
				AmountOfPEs => AmountOfPEs,
				PEAddresses => PEAddresses,
                SelfIndex   => i,
				SelfAddress => PEAddresses(i)
			)

			port map(

				-- Basic
				Clock => Clock,
				Reset => Reset,

				-- PE interface (Bridge input)
				ClockRx => PEOutputs(i).ClockTx,
				Rx      => PEOutputs(i).Tx,
				DataIn  => PEOutputs(i).DataOut,
				CreditO => PEInputs(i).CreditI,

				-- Crossbar interface (Bridge output)
				ClockTx => open,
				Tx      => bridgeTx(i),
				DataOut => bridgeDataOut(i),
				CreditI => bridgeCreditI(i),

				-- Arbiter interface
				ACK     => bridgeACK(i),
				Request => bridgeRequest(i),
				Grant   => bridgeGrant(i)

			);

	end generate CrossbarBridgeGen;


	-- Instantiates switch controllers
	CrossbarControlGen: for i in 0 to AmountOfPEs - 1 generate

		CrossbarControl: entity work.CrossbarControl

			generic map(
				AmountOfPEs => AmountOfPEs
			)
			port map(
				
				-- Basic
				Clock => Clock,
				Reset => Reset,

				-- Arbiter Interface
				ACK => arbiterACK(i),
				Grant => arbiterGrant(i),

				-- Switch Interface
				SwitchEnable => switchEnable(i),
				SwitchSelect => switchSelect(i)

			);

	end generate CrossbarControlGen;

	-- Instantiates arbiters as given by "ArbiterType" generic
	ArbiterGen: for Arbiter in 0 to AmountOfPEs - 1 generate

		ArbiterFactory: entity work.ArbiterFactory

			generic map(
				ArbiterType => ArbiterType,
				AmountOfPEs => AmountOfPEs
			)

			port map(
				
				Clock => Clock,
				Reset => Reset,

                ACK   => arbiterACK(Arbiter),
                Grant => arbiterGrant(Arbiter),
                Req   => arbiterRequest(Arbiter)

			);

	end generate ArbiterGen;

	Switch: for PE in 0 to AmountOfPEs - 1 generate

		-- Makes data links, ignoring links to self
		DataLinksGen: for Bridge in 0 to AmountOfPEs - 1 generate

            DataLinkMap: if PE /= Bridge generate

			    PEInputs(PE).DataIn <= bridgeDataOut(Bridge) when switchSelect(PE)(Bridge) = '1' else (others => 'Z');
			    PEInputs(PE).Rx <= bridgeTx(Bridge) when switchSelect(PE)(Bridge) = '1' else 'Z';
			    bridgeCreditI(Bridge) <= PEOutputs(PE).CreditO when switchSelect(PE)(Bridge) = '1' else 'Z';

            end generate DataLinkMap;

		end generate DataLinksGen;

		-- Makes arbiter request connections, ignoring requests to self
		RequestGen: for Bridge in 0 to AmountOfPEs - 1 generate

			RequestMap: if PE /= Bridge generate
				arbiterRequest(PE)(Bridge) <= bridgeRequest(Bridge)(PE); 
			end generate RequestMap;

			RequestGround: if PE = Bridge generate
				arbiterRequest(PE)(Bridge) <= '0';
			end generate RequestGround;

		end generate RequestGen;

		-- Makes arbiter links
		--bridgeGrant(PE) <= orReduce(switchSelect(PE));

		ACKLinkGen: for Bridge in 0 to AmountOfPEs - 1 generate

			ACKMap: if PE /= Bridge generate
			    bridgeGrant(Bridge) <= arbiterGrant(PE)(Bridge) when switchSelect(PE)(Bridge) = '1' else 'Z';
				arbiterACK(PE) <= bridgeACK(Bridge) when switchSelect(PE)(Bridge) = '1' else 'Z';
			end generate ACKMap;

		end generate ACKLinkGen;

	end generate Switch;

end architecture RTL;
