
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;


entity ClockDivider is

	generic(
		CounterBitWidth: integer
	);

	port(

		Clock: in std_logic;
		Reset: in std_logic;

		N: in std_logic_vector(CounterBitWidth - 1 downto 0);
		M: in std_logic_vector(CounterBitWidth - 1 downto 0);
		WriteEnable: in std_logic;

		ClockGated: out std_logic

	);
	
end entity ClockDivider;


architecture RTL of ClockDivider is

	signal NReg, MReg, MResetValue: unsigned(CounterBitWidth - 1 downto 0);

begin

	ClockGated <= Clock when NReg <= MReg else '0';

	-- Decreases M by 1 and compares to N, reset M to its max value when it reaches 0
	process(Clock, Reset) begin

		if Reset = '1' then

			-- Defaults to slowest possible clock
			NReg <= (0 => '1', others => '0');
			MReg <= (others => '1');

		elsif rising_edge(Clock) then

			if WriteEnable = '1' then

				NReg <= unsigned(N);
				MReg <= unsigned(M);
				MResetValue <= unsigned(M);

			else

				if MReg = 1 then
					MReg <= MResetValue;
				else
					MReg <= MReg - 1;
				end if;

			end if;

		end if;

	end process;
	
end architecture RTL;
