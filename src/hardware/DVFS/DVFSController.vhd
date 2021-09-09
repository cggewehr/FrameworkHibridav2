--------------------------------------------------------------------------------
-- Title       : DVFS Controller for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : DVFSController.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : 
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        :
--------------------------------------------------------------------------------


library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	use ieee.math_real.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
    --use work.JSON.all;
	--use work.HyHeMPS_PKG.all;


entity DVFSController is

	generic(
		DVFSServiceCode: DataWidth_t := x"0000FFFF";
		AmountOfVoltageLevels: integer := 2;
		CounterBitWidth: integer := 5;
		BaseNoCPos: HalfDataWidth_t := x"0F0F";
		IsNoC: boolean := True
	);

	port(
		
		Clock: in std_logic;
		Reset: in std_logic;

		ClockToCommStruct: out std_logic;

		SupplySwitchesEnable: out std_logic_vector(AmountOfVoltageLevels - 1 downto 0);

		LocalPortData: in DataWidth_t;
		LocalPortTX: in std_logic;
		LocalPortCreditI: in std_logic;
		LocalPortClockTX: in std_logic

	);
	
end entity DVFSController;


architecture RTL of DVFSController is

	-- Size of Voltage Level field
	constant Log2OfVoltageSwitchField: integer := integer(ceil(log2(real(AmountOfVoltageLevels))));

	-- Info flit fields (field bit width below):
	-- |        Voltage Level        | IsNoC | ... |         N         |         M         |
	--   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
	alias SupplyVoltageSwitchToTurnONAsync: std_logic_vector(Log2OfVoltageSwitchField - 1 downto 0) is LocalPortData(DataWidth - 1 downto DataWidth - Log2OfVoltageSwitchField);
	alias IsNoCBit: std_logic is LocalPortData(DataWidth - 1 - Log2OfVoltageSwitchField);
	alias DividerNAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData((2*CounterBitWidth) - 1 downto CounterBitWidth); 
	alias DividerMAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData(CounterBitWidth - 1 downto 0);

	-- Clock Divider pulses (1, 1/2, 1/4, ...)
	--signal dividedClocks: std_logic_vector(Log2OfVoltageSwitchField - 1 downto 0); 
	signal dividedClocks: std_logic_vector(AmountOfVoltageLevels - 1 downto 0); 
	
	-- Clock Gating interface registers
	--signal DividerCounterReg, DividerNReg, DividerMReg: std_logic_vector(CounterBitWidth - 1 downto 0);
    signal dividerNShifted: std_logic_vector(CounterBitWidth - 1 downto 0);
	signal clockEnable: std_logic;

    -- Supply switch enables
    signal supplySwitchReg: std_logic_vector(AmountOfVoltageLevels - 1 downto 0);
    signal supplySwitchSyncReg: std_logic_vector(AmountOfVoltageLevels - 1 downto 0);

	-- Control signals
	type ControllerState_t is (Sidle, Ssize, Sservice, SvaluesOfInterest, SwaitUntilMSGFinished);
	signal ControllerState: ControllerState_t;
    signal syncGoAhead: std_logic;
    signal writeEnable: std_logic;

    signal ClockTristate: std_logic;

begin

	-- Propagates clock when N < M
	GatedClock: ClockToCommStruct <= ClockTristate when clockEnable = '1' else '0';

	ClockTristateGen: for i in AmountOfVoltageLevels - 1 downto 0 generate
        ClockTristate <= dividedClocks(i) when supplySwitchReg(i) = '1' else 'Z';
    end generate ClockTristateGen;
    
    -- Generates Clock pulses
    ClockDivider: entity work.ClockDivider

        generic map(
            --DividerDepth => Log2OfVoltageSwitchField
            DividerDepth => AmountOfVoltageLevels
        )
        port map(
            MainClock => Clock,
            Reset => Reset,
            DividedClocks => dividedClocks
        );

    -- Generates Clock gating enable signal
    --dividerNShifted <= std_logic_vector(shift_left(unsigned(DividerNAsync), to_integer(unsigned(SupplyVoltageSwitchToTurnONAsync))));
    dividerNShifted <= std_logic_vector(shift_left(unsigned(DividerNAsync), 1)) when SupplyVoltageSwitchToTurnONAsync = "0" else DividerNAsync;
    ClockGatingCounter: entity work.ClockGatingCounter

        generic map(
            CounterBitWidth => CounterBitWidth
        )
        port map(

            Clock => Clock,
            Reset => Reset,

            N => dividerNShifted,
            M => DividerMAsync,
            WriteEnable => writeEnable,

            SyncGoAhead => syncGoAhead,

            ClockEnable => clockEnable
        );

    -- Registers the decoded output of power switch enable signals
    SupplySwitchesEnable <= supplySwitchReg;

    SupplySwitchSync: process(Clock, Reset) begin

        if Reset = '1' then

            -- Defaults to highest voltage
            supplySwitchReg <= (others => '0');
            supplySwitchReg(AmountOfVoltageLevels - 1) <= '1';

        --elsif rising_edge(Clock) then
        elsif rising_edge(Clock) then

            if SyncGoAhead = '1' then
                supplySwitchReg <= supplySwitchSyncReg;
            end if;

        end if;

    end process SupplySwitchSync;

    -- Syncs switch enable regs with N by M ratio
	SupplySwitchEnableRegs: process(LocalPortClockTX, Reset) begin

        --if rising_edge(Clock) then
        if rising_edge(LocalPortClockTX) then

            if WriteEnable = '1' then

                --supplySwitchSyncReg <= decode(SupplyVoltageSwitchToTurnONAsync);
                if SupplyVoltageSwitchToTurnONAsync = "1" then
                     supplySwitchSyncReg <= "10";
                else
                     supplySwitchSyncReg <= "01";
                end if;

            end if;

        end if;

    end process;

	-- Controls writing of signals to counter & switch regs
	DVFSStateMachine: process(LocalPortClockTX, Reset) 
        variable NAsInt, MAsInt: integer;  -- Integer representation on N and M (for asserts at the end)
    begin

        -- Defaults to highest clock frequency possible, ensuring required throughput is always given until a DVFS packet arrives
		if Reset = '1' then

			ControllerState <= Sidle;

		elsif rising_edge(LocalPortClockTX) then

			-- Waits for new packet at local port
			if ControllerState = Sidle then

				--if LocalPortData(HalfDataWidth - 1 downto 0) = BaseNoCPos and LocalPortTX = '1' and LocalPortCreditI = '1' then
				if LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= Ssize;
				else
					ControllerState <= Sidle;
				end if;

			-- Waits for first payload flit
			elsif ControllerState = Ssize then

				if LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= Sservice;
				else
					ControllerState <= Ssize;
				end if;

			-- Compares first payload flit to established DVFS service ID (known at elab time)
			elsif ControllerState = Sservice then

				if LocalPortTX = '1' and LocalPortCreditI = '1' then

                    if LocalPortData = DVFSServiceCode then
					    ControllerState <= SvaluesOfInterest;
				    else
					    ControllerState <= SwaitUntilMSGFinished;
                    end if;

				end if;

			-- Sets voltage switches and clock divider ratio, as defined by the 2nd flit of 
			elsif ControllerState = SvaluesOfInterest then

                ControllerState <= SwaitUntilMSGFinished;

                -- Certifies switch to be enabled is coherent with N/M values (ONLY FOR AmountOfVoltageLevels = 2)
                NAsInt := to_integer(unsigned(DividerNAsync));
                MAsInt := to_integer(unsigned(DividerMAsync));
                assert not (AmountOfVoltageLevels = 2 and SupplyVoltageSwitchToTurnONAsync = "1" and NAsInt <= MAsInt/2) report "High voltage supply switch enabled for N/M <= 1/2: <" & integer'image(NAsInt) & "/" & integer'image(MAsInt) & ">" severity error;
                assert not (AmountOfVoltageLevels = 2 and SupplyVoltageSwitchToTurnONAsync = "0" and NAsInt > MAsInt/2) report "Low voltage supply switch enabled for N/M > 1/2: <" & integer'image(NAsInt) & "/" & integer'image(MAsInt) & ">" severity error;

			-- Waits for end of packet
			elsif ControllerState = SwaitUntilMSGFinished then

				if LocalPortTX = '1' then
					ControllerState <= SwaitUntilMSGFinished;
				else
					ControllerState <= Sidle;
				end if;

			end if;

		end if;

	end process;

    -- Combinationally determines the write enable signals for supply switch and divider regs (<= info from 2nd payload flit)
    writeEnable <= '1' when ControllerState = SvaluesOfInterest and ((IsNoC and IsNoCBit = '1') or ((not IsNoc) and IsNoCBit = '0')) else '0';

	-- Certifies field widths are coherent with DataWidth (only involves constants, should only run at 0 simulation time)
	assert not ((2 * CounterBitWidth) + Log2OfVoltageSwitchField + 1 > DataWidth) report "Amount of Voltage Levels and Counter Values exceed platform bit width: 2*" & integer'image(CounterBitWidth) & " + " & integer'image(Log2OfVoltageSwitchField) & " + 1 > " & integer'image(DataWidth) severity failure;

    --NAsInt <= to_integer(unsigned(DividerNAsync));
    --MAsInt <= to_integer(unsigned(DividerMAsync));
    --assert not (AmountOfVoltageLevels = 2 and ControllerState = SvaluesOfInterest and SupplyVoltageSwitchToTurnONAsync = "1" and NAsInt <= MAsInt/2) report "High voltage supply switch enabled for N/M <= 1/2: <" & integer'image(NAsInt) & "/" & integer'image(MAsInt) & ">" severity error;
    --assert not (AmountOfVoltageLevels = 2 and ControllerState = SvaluesOfInterest and SupplyVoltageSwitchToTurnONAsync = "0" and NAsInt > MAsInt/2) report "Low voltage supply switch enabled for N/M > 1/2: <" & integer'image(NAsInt) & "/" & integer'image(MAsInt) & ">" severity error;
	
end architecture RTL;
