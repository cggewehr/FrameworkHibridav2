--------------------------------------------------------------------------------
-- Title       : Bus control module for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : BusControl.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : 
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Gewehr: Initial implementation
--------------------------------------------------------------------------------
-- TODO        : Constraint flitCounter to data width
--------------------------------------------------------------------------------


library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;


entity BusControl is

	generic(
	    AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector
	);

	port (

		-- Basic
		Clock      : in std_logic;
		Reset      : in std_logic;

		-- Bus interface
		BusTx      : inout std_logic;
		BusData    : inout DataWidth_t;
		BusCredit  : inout std_logic;

		-- PE interface
		PERx       : out std_logic_vector(0 to AmountOfPEs - 1);
		PECredit   : in std_logic_vector(0 to AmountOfPEs - 1)

	);
	
end entity BusControl;


architecture RTL of BusControl is

	-- FSM states
	type state_t is (Sreset, Sstandby, Ssize, Spayload);
	signal currentState: state_t;

	-- Contains size of current msg's payload. Decremented by one every time a flit is sent across the bus, until msg has been fully sent
	signal flitCounter: integer;

	-- Contains index of current message target PE's address in PEAddresses generic
	signal targetIndex: integer;

	-- Flags there is a message being sent through the bus. Used in switching PERx and BusCredit  
	signal busBeingUsed: std_logic;

	-- Returns index of a given element in a given array
	function GetIndexOfAddr(Addresses: HalfDataWidth_vector; AddressOfInterest: HalfDataWidth_t) return integer is begin

		for i in 0 to Addresses'high - 1 loop  -- Ignores wrapper (Last element of Addresses[])

			if Addresses(i) = AddressOfInterest then
				return i;

			end if;

		end loop;

		return Addresses'high;  -- Return index of wrapper if given ADDR was not found in bus
		
	end function GetIndexOfAddr;

begin

	-- Moore FSM, controls input interface of target PE as longs as the current message is being transmitted
	process(Clock)  -- Synchronous reset

		--  1st flit of a message, to be translated into an index, through GetIndexOfAddr(). 
		-- This index is then registered in register of bit width proportional to the amount of PEs in this bus
		-- Registering targetIndex instead of targetAddr implies synthesizing a smaller bit width register 
		-- (targetAddr must be as wide as a flit, but not targetIndex) 
		variable targetAddr: HalfDataWidth_t;

	begin

		if rising_edge(Clock) then

			if Reset = '1' then

				busBeingUsed <= '0';

				currentState <= Sreset;

			end if;

			-- Sets default values
			if currentState = Sreset then

				targetIndex <= 0;
				flitCounter <= 0;

				currentState <= Sstandby;

			-- Checks for a new transmission. If so, determine targetIndex from 1st flit of msg and proceed, else, wait for transmission
			elsif currentState = Sstandby then

				if BusTx = '1' then

                    -- PE ID @ most significative bits of first flit
					targetAddr := BusData(DataWidth - 1 downto HalfDataWidth);
					targetIndex <= GetIndexOfAddr(PEAddresses, targetAddr);
					busBeingUsed <= '1';

					currentState <= Ssize;
				
				else
					currentState <= Sstandby;

				end if;

			-- Initialize flitCounter from 2nd flit of msg (which contains payload size)
			elsif currentState = Ssize then

				flitCounter <= to_integer(unsigned(BusData));

				currentState <= Spayload;

			-- Remains in this state until all payload flits have been transmitted
			elsif currentState = Spayload then

				-- Checks if a flit was transmitted
				--if PECredit(targetIndex) = '1' and BusTx = '1' then
				if BusCredit = '1' and BusTx = '1' then
					flitCounter <= flitCounter - 1;

				end if;

				-- Determines if this is the last flit of msg
				--if flitCounter = 1 and PECredit(targetIndex) = '1' and BusTx = '1' then
				if flitCounter = 1 and BusCredit = '1' and BusTx = '1' then

					busBeingUsed <= '0';
					currentState <= Sstandby;

				else
					currentState <= Spayload;

				end if;

			end if;

		end if;

	end process;

	-- Active only after 1st flit of current messages (containing ADDR of target) is known
	--PERx <= (targetIndex => BusTx, others => '0') when busBeingUsed = '1' else (others => '0');

	-- BusCredit gets Credit_o of msg target PE
	--BusCredit <= PECredit(targetIndex) when busBeingUsed = '1' else '0';

	process(busBeingUsed, targetIndex, PECredit) begin  -- (Describes same behaviour, but compatible with Cadence tools)

		PERx <= (others => '0');

		if busBeingUsed = '1' then
			PERx(targetIndex) <= BusTx;

		end if;

		if busBeingUsed = '1' then
			BusCredit <= PECredit(targetIndex);
		else
			BusCredit <= '0';
		end if;

	end process;


end architecture RTL;
