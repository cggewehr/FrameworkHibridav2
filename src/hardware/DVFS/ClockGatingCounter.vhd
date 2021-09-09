
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;


entity ClockGatingCounter is

	generic(
		CounterBitWidth: integer
	);

	port(

		Clock: in std_logic;
		Reset: in std_logic;

		N: in std_logic_vector(CounterBitWidth - 1 downto 0);
		M: in std_logic_vector(CounterBitWidth - 1 downto 0);
		WriteEnable: in std_logic;

		SyncGoAhead: out std_logic;

		ClockEnable: out std_logic

	);
	
end entity ClockGatingCounter;


architecture RTL of ClockGatingCounter is

	signal NCounterReg, MCounterReg, DividerCounterReg: unsigned(CounterBitWidth - 1 downto 0);
	signal ComparatorReg: std_logic;

	signal NSyncReg, MSyncReg, SyncCounterReg: unsigned(CounterBitWidth - 1 downto 0);
	signal SyncFlagReg, SyncInitialized: std_logic;

begin

	--
	SyncRegs: process(Clock, Reset) begin

		if Reset = '1' then

			NSyncReg <= (others => '1');
			MSyncReg <= (others => '1');
            SyncInitialized <= '0';

		elsif rising_edge(Clock) then

			if WriteEnable = '1' then

				NSyncReg <= unsigned(N);
				MSyncReg <= unsigned(M);
                SyncInitialized <= '1';

            --elsif SyncGoAhead = '1' then
            elsif SyncFlagReg = '1' and SyncInitialized = '1'then
                SyncInitialized <= '0';

			end if;

		end if;

	end process;

	--
	SyncCounter: process(Clock, Reset) begin

		if Reset = '1' then
			SyncCounterReg <= (others => '0');

		elsif rising_edge(Clock) then
            
			-- SyncCounter++
			SyncCounterReg <= to_unsigned(incr(to_integer(SyncCounterReg), (2**CounterBitWidth) - 1, 0), CounterBitWidth);

		end if;

	end process;

	--
    SyncGoAhead <= SyncFlagReg and SyncInitialized;
    SyncFlagReg <= '1' when SyncCounterReg = (CounterBitWidth - 1 downto 0 => '1') else '0';
	--SyncComparator: process(Clock, Reset) begin

		--if Reset = '1' then
		--	SyncFlagReg <= '0';

		--elsif rising_edge(Clock) then

		--	if SyncCounterReg = 0 then
		--		SyncFlagReg <= '1';
		--	else
		--		SyncFlagReg <= '0';
		--	end if; 

		--end if;

	--end process;

	-- Propagates clock when N < M
	--GatedClock: ClockGated <= Clock when ComparatorReg = '1' else '0';

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
            --if WriteEnable = '1' then
            if SyncFlagReg = '1' then
                DividerCounterReg <= (others => '0');
            else
			    DividerCounterReg <= to_unsigned(incr(to_integer(DividerCounterReg), to_integer(MCounterReg) - 1, 0), CounterBitWidth);
            end if;

		end if;

	end process;

	-- Compares CounterReg to N
    ClockEnable <= ComparatorReg;
    --ComparatorReg <= '1' when DividerCounterReg < NCounterReg else '0';
	DividerComparator: process(Clock, Reset) begin

		if Reset = '1' then
			ComparatorReg <= '0';

		--elsif rising_edge(Clock) then
		elsif falling_edge(Clock) then

			if DividerCounterReg < NCounterReg then
				ComparatorReg <= '1';
			else
				ComparatorReg <= '0';
			end if; 

		end if;

	end process;

    -- Ensures N <= M for every new write
    --assert not (NCounterReg > MCounterReg) report "New N value <" & integer'image(to_integer(NCounterReg)) & "> greater then new M value <" & integer'image(to_integer(MCounterReg)) & ">" severity error;

end architecture RTL;
