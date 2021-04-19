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
		DVFSServiceCode: DataWidth_t;
		AmountOfVoltageLevels: integer;
		CounterBitWidth: integer;
		BaseNoCPos: HalfDataWidth_t;
		IsNoC: boolean
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
	alias IsNoCBit: std_logic is LocalPortData(Log2OfVoltageSwitchField - 1);
	alias DividerNAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData((2*CounterBitWidth) - 1 downto CounterBitWidth); 
	alias DividerMAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData(CounterBitWidth - 1 downto 0);

	-- Divider control signals
	signal DividerClockGated: std_logic; 
	signal DividerWriteEnable: std_logic; 

	-- Control FSM
	type ControllerState_t is (Sidle, Ssize, Sservice, SvaluesOfInterest, SwaitUntilMSGFinished);
	signal ControllerState: ControllerState_t;

begin

	-- Instantiate N/M Clock Divider
	ClockDivider: entity work.ClockDivider

		generic map(
			CounterBitWidth => CounterBitWidth
		)

		port map(

			Clock => Clock,
			Reset => Reset,

			N => DividerNAsync,
			M => DividerMAsync,
			WriteEnable => DividerWriteEnable,

			ClockGated => DividerClockGated

		);

	--ClockGate: process(Clock) begin

	--	if rising_edge(Clock) or falling_edge(Clock) then 
	--		ClockToCommStruct <= DividerClockGated;
	--	end if;

	--end process ClockGate;
	ClockToCommStruct <= DividerClockGated;

	-- Controls writing of signals to counter & switch regs
	DVFSStateMachine: process(LocalPortClockTX, Reset) begin

		if Reset = '1' then

			-- Defaults to lowest gated frequency (N/M = 1/CounterResolution)
			DividerWriteEnable <= '0';

			-- Defaults to lowest voltage
            SupplySwitchesEnable <= (others => '0');
            SupplySwitchesEnable(0) <= '1';

			ControllerState <= Sidle;

		elsif rising_edge(LocalPortClockTX) then

			-- Waits for new packet at local port
			if ControllerState = Sidle then

				if LocalPortData(HalfDataWidth - 1 downto 0) = BaseNoCPos and LocalPortTX = '1' and LocalPortCreditI = '1' then
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

			-- Compares first payload flit to established DVFS service ID
			elsif ControllerState = Sservice then

				if LocalPortData = DVFSServiceCode and LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= SvaluesOfInterest;
				else
					ControllerState <= SwaitUntilMSGFinished;
				end if;

			-- Sets voltage switches and clock divider ratio 
			elsif ControllerState = SvaluesOfInterest then

				if (IsNoC and IsNoCBit = '1') or ((not IsNoc) and IsNoCBit = '0') then

					DividerWriteEnable <= '1';
					SupplySwitchesEnable <= decode(SupplyVoltageSwitchToTurnONAsync);

					ControllerState <= SwaitUntilMSGFinished;

				end if;

			-- Waits for end of packet
			elsif ControllerState = SwaitUntilMSGFinished then

				if LocalPortTX = '0' then
					ControllerState <= Sidle;
				else
					ControllerState <= SwaitUntilMSGFinished;
				end if;

			end if;

		end if;

	end process;

	-- Certifies field widths are coherent with DataWidth
	assert not ((2 * CounterBitWidth) + AmountOfVoltageLevels + 1 >= DataWidth) report "Amount of Voltage Levels and Counter Values exceed platform bit witdh: 2*" & integer'image(CounterBitWidth) & " + " & integer'image(AmountOfVoltageLevels) & ">" & integer'image(DataWidth) severity FAILURE;
	
end architecture RTL;
