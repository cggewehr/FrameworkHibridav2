
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
		BaseNoCPos: HalfDataWidth_t
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

	alias DividerNAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData((2*CounterBitWidth) - 1 downto CounterBitWidth); 
	alias DividerMAsync: std_logic_vector(CounterBitWidth - 1 downto 0) is LocalPortData(CounterBitWidth - 1 downto 0);
	signal DividerClockGated: std_logic; 
	signal DividerWriteEnable: std_logic; 

	constant Log2OfVoltageSwitchField: integer := integer(ceil(log2(real(AmountOfVoltageLevels))));
	alias SupplyVoltageSwitchToTurnONAsync: std_logic_vector(Log2OfVoltageSwitchField - 1 downto 0) is LocalPortData(DataWidth - 1 downto DataWidth - Log2OfVoltageSwitchField);

	type ControllerState_t is (Sidle, Ssize, Sservice, SvaluesOfInterest, SwaitUntilMSGFinished);
	signal ControllerState: ControllerState_t;

begin

	-- Instantiate Clock Divider
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

	ClockGate: process(Clock) begin

		if rising_edge(Clock) then 
			ClockToCommStruct <= DividerClockGated;
		end if;

	end process ClockGate;

	-- Controls writing of signals to counter & switch regs
	DVFSStateMachine: process(LocalPortClockTX, Reset) begin

		if Reset = '1' then

			DividerWriteEnable <= '0';

			--SupplySwithesEnable <= (0 => '1', others => '0');
            SupplySwitchesEnable <= (others => '0');
            SupplySwitchesEnable(0) <= '1';

			ControllerState <= Sidle;

		elsif rising_edge(LocalPortClockTX) then

			if ControllerState = Sidle then

				if LocalPortData(DataWidth - 1 downto HalfDataWidth) = BaseNoCPos and LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= Ssize;
				else
					ControllerState <= Sidle;
				end if;

			elsif ControllerState = Ssize then

				if LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= Sservice;
				else
					ControllerState <= Ssize;
				end if;

			elsif ControllerState = Sservice then

				if LocalPortData = DVFSServiceCode and LocalPortTX = '1' and LocalPortCreditI = '1' then
					ControllerState <= SvaluesOfInterest;
				else
					ControllerState <= SwaitUntilMSGFinished;
				end if;

			elsif ControllerState = SvaluesOfInterest then

				DividerWriteEnable <= '1';

				SupplySwitchesEnable <= decode(SupplyVoltageSwitchToTurnONAsync);

				ControllerState <= SwaitUntilMSGFinished;

			elsif ControllerState = SwaitUntilMSGFinished then

				if LocalPortTX = '0' then
					ControllerState <= Sidle;
				else
					ControllerState <= SwaitUntilMSGFinished;
				end if;

			end if;

		end if;

	end process;

	assert not ((2 * CounterBitWidth) + AmountOfVoltageLevels > DataWidth) report "Amount of Voltage Levels and Counter Values exceed platform bit witdh: 2*" & integer'image(CounterBitWidth) & " + " & integer'image(AmountOfVoltageLevels) & ">" & integer'image(DataWidth) severity FAILURE;
	
end architecture RTL;
