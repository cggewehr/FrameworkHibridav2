
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;


entity ClockDivider is

	generic(
		DividerDepth: integer
	);

	port(

		MainClock: in std_logic;
        Reset: in std_logic;

		DividedClocks: inout std_logic_vector(DividerDepth - 1 downto 0)

	);
	
end entity ClockDivider;


architecture RTL of ClockDivider is 

    -- Produces a clock signal with a frequency of half of its input clock signal
    procedure DivideBy2(

        signal Reset: in std_logic; 
        signal InClock: in std_logic; 
        signal OutClock: inout std_logic) is 

    begin

        if Reset = '1' then
            OutClock <= '0';

        elsif rising_edge(InClock) then
            OutClock <= not OutClock;

        end if;

    end procedure DivideBy2;

begin

    DividedClocks(DividerDepth - 1) <= MainClock;

    DividerGen: for i in 0 to DividerDepth - 2 generate
        DivideBy2(Reset, DividedClocks(i + 1), DividedClocks(i));
    end generate DividerGen;

end architecture RTL;
