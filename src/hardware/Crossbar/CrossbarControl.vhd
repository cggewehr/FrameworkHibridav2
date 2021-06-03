--------------------------------------------------------------------------------
-- Title       : Crossbar interface module for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : CrossbarControl.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Handles messages from Crossbar to PE
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--             : v0.02 - Use arbiter grant signal to determine msg source, reducing complexity 
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


entity CrossbarControl is

	generic (
		AmountOfPEs: integer
	);
	port (
		
		-- Basic
		Clock: in std_logic;
		Reset: in std_logic;

		-- Arbiter Interface
		ACK: in std_logic;
		Grant: in std_logic_vector(0 to AmountOfPEs - 1);

		-- Switch Interface
		SwitchEnable: out std_logic;
		SwitchSelect: out std_logic_vector(0 to AmountOfPEs - 1)

	);
	
end entity CrossbarControl;


architecture RTL of CrossbarControl is

begin

	SwitchSelect <= Grant;

	process(Clock, Reset) begin

        if Reset = '1' then
            SwitchEnable <= '0';

		elsif rising_edge(Clock) then

			if ACK = '1' then
            	SwitchEnable <= '0';

			elsif Grant /= (others => '0') then
				SwitchEnable <= '1';

			end if;

		end if;

	end process;
	
end architecture RTL;
