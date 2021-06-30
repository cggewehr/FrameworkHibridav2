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

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all; 


entity BusControl is

	generic(
	    AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector
	);

	port (

		-- Basic
		Clock    : in std_logic;
		Reset    : in std_logic;

		-- Bus interface
		BusTx    : in std_logic;
		BusData  : in DataWidth_t;

        -- Arbiter interface
        ACK      : in std_logic;

		-- PE rx-side control interface
		RXEnable : out std_logic_vector(0 to AmountOfPEs - 1)

	);
	
end entity BusControl;


architecture RTL of BusControl is

	-- FSM states
	--type state_t is (Sstandby, SsetControl, SwaitForACK);
	type state_t is (Sstandby, SwaitForACK);
	signal currentState: state_t;

	-- Returns index of a given element in a given array
	function GetIndexOfAddr(Addresses: HalfDataWidth_vector; AddressOfInterest: HalfDataWidth_t) return integer is begin

		for i in 0 to Addresses'high - 1 loop  -- Ignores wrapper (Last element of Addresses[])

			if Addresses(i) = AddressOfInterest then
				return i;

			end if;

		end loop;

		return Addresses'high;  -- Return index of wrapper (always @ the greatest posiition) if given ADDR was not found in bus
		
	end function GetIndexOfAddr;

begin

	-- Moore FSM, controls input interface of target PE as longs as the current message is being transmitted
	process(Clock, Reset)  -- Synchronous reset

		--  1st flit of a message, to be translated into an index, through GetIndexOfAddr(). 
		-- This index is then registered in register of bit width proportional to the amount of PEs in this bus
		-- Registering targetIndex instead of targetAddr implies synthesizing a smaller bit width register 
		-- (targetAddr must be as wide as a flit, but not targetIndex) 
		variable targetAddr: HalfDataWidth_t;

	    -- Contains index of current message target PE's address in PEAddresses generic
        variable targetIndex: integer range 0 to AmountOfPEs - 1;

	begin

        -- Sets default values
        if Reset = '1' then

			RXEnable <= (others => '0');

			currentState <= Sstandby;
		
        elsif rising_edge(Clock) then
				
			-- Checks for a new transmission. If so, determine targetIndex from 1st flit of msg and proceed, else, wait for transmission
			case currentState is

                 when Sstandby =>

			        RXEnable <= (others => '0');

				    if BusTx = '1' then

                        -- PE ID @ most significative bits of first flit
					    targetAddr := BusData(DataWidth - 1 downto HalfDataWidth);
					    targetIndex := GetIndexOfAddr(PEAddresses, targetAddr);
					    --RXEnable(GetIndexOfAddr(PEAddresses, targetAddr)) <= '1';
					    RXEnable(targetIndex) <= '1';

					    --currentState <= SsetControl;
					    currentState <= SwaitForACK;
				
				    else
					    currentState <= Sstandby;
				    end if;

                -- Sets tristate enables for Credit signal on RX side
                --when SsetControl =>
     
			        --RXEnable(targetIndex) <= '1';
                    
                    --currentState <= SwaitForACK;
        
                -- Wait for packet to be fully transmited through the Bus
                when SwaitForACK =>

                    if ACK = '1' then
			            RXEnable <= (others => '0');
                        currentState <= Sstandby;
                    else
                        currentState <= SwaitForACK;
                    end if;

			end case;

		end if;

	end process;

end architecture RTL;
