
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;


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

	signal NCounterReg, MCounterReg, DividerCounterReg: unsigned(CounterBitWidth - 1 downto 0);
	signal ComparatorReg: std_logic;

	signal NSyncReg, MSyncReg, SyncCounterReg: unsigned(CounterBitWidth - 1 downto 0);
	signal SyncFlagReg: std_logic;

begin

	--
	SyncRegs: process(Clock, Reset) begin

		if Reset = '1' then

			NSyncReg <= (others => '1');
			MSyncReg <= (others => '1');

		elsif rising_edge(Clock) then

			if WriteEnable = '1' then

				NSyncReg <= unsigned(N);
				MSyncReg <= unsigned(M);

			end if;

		end if;

	end process;

	--
	SyncCounter: process(Clock, Reset) begin

		if Reset = '1' then
			SyncCounterReg <= (others => '0');

		elsif rising_edge(Clock) then
			SyncCounterReg <= to_unsigned(incr(to_integer(SyncCounterReg), (2**CounterBitWidth) - 1, 0), CounterBitWidth);

		end if;

	end process;

	--
	SyncComparator: process(Clock, Reset) begin

		if Reset = '1' then
			SyncFlagReg <= '0';

		elsif rising_edge(Clock) then

			if SyncCounterReg = 0 then
				SyncFlagReg <= '1';
			else
				SyncFlagReg <= '0';
			end if; 

		end if;

	end process;

	-- Propagates clock when N < M
	GatedClock: ClockGated <= Clock when ComparatorReg = '1' else '0';

	-- Control writing to N and M registers
	CounterRegs: process(Clock, Reset) begin

		if rising_edge(Clock) then

			if SyncFlagReg = '1' then

				NCounterReg <= NSyncReg;
				MCounterReg <= MSyncReg;

			end if;

		end if;

	end process;

	-- Counts from 0 to M - 1 
	DividerCounter: process(Clock, Reset) begin

		if Reset = '1' then

			DividerCounterReg <= (others => '0');

		elsif rising_edge(Clock) then

			-- Counter++ mod M
            if WriteEnable = '1' then
                DividerCounterReg <= (others => '0');
            else
			    DividerCounterReg <= to_unsigned(incr(to_integer(DividerCounterReg), to_integer(MCounterReg) - 1, 0), CounterBitWidth);
            end if;

		end if;

	end process;

	-- Compares CounterReg to N
	DividerComparator: process(Clock, Reset) begin

		if Reset = '1' then

			ComparatorReg <= '0';

		elsif rising_edge(Clock) then

			if DividerCounterReg < NCounterReg then
				ComparatorReg <= '1';
			else
				ComparatorReg <= '0';
			end if; 

		end if;

	end process;

    -- Ensures N <= M for every new write
    assert not (NReg > MReg) report "New N value <" & integer'image(to_integer(NReg)) & "> greater then new M value <" & integer'image(to_integer(MReg)) & ">" severity error;

end architecture RTL;
