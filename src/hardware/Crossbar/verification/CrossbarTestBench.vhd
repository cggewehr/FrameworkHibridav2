--------------------------------------------------------------------------------
-- Title       : <Title Block>
-- Project     : Default Project Name
--------------------------------------------------------------------------------
-- File        : CrossbarTestBench.vhd
-- Author      : User Name <user.email@user.company.com>
-- Company     : User Company Name
-- Standard    : <VHDL-2008 | VHDL-2002 | VHDL-1993 | VHDL-1987>
-------------------------------------------------------------------------------
-- Description: 
--------------------------------------------------------------------------------
-- Revisions:  Revisions and documentation are controlled by
-- the revision control system (RCS).  The RCS should be consulted
-- on revision history.
-------------------------------------------------------------------------------


library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;


entity CrossbarTestBench is
	
end entity CrossbarTestBench;


architecture RTL of CrossbarTestBench is

	signal clock: std_logic := '0';
	constant ClockPeriod: time := 10 ns;  -- 100 MHz

	signal reset: std_logic := '1';

	constant AmountOfPEs: integer := 9;
	constant PEAddresses: HalfDataWidth_vector(0 to AmountOfPEs - 1) := (x"0000", x"0100", x"0200", x"0001", x"0101", x"0201", x"0002", x"0102", x"0202");

	signal PEInterfaces: PEInterface_vector(0 to AmountOfPEs - 1);
	
	constant ProjPath: string := "D:/Xilinx/Projects/HyHeMPS_Bus/";

begin

    ResetGen: reset <= '0' after ClockPeriod/2 + 100 ns;

	ClockGen: process begin

		wait for ClockPeriod/2;
		clock <= not clock; 

	end process ClockGen;


	PEGen: for i in 0 to AmountOfPEs - 1 generate

		PE: entity work.PE

			generic map(
				PEConfigFile => ProjPath & "flow/PE" & integer'image(i) & ".json",
		        InjectorConfigFile => ProjPath & "flow/INJ" & integer'image(i) & ".json",
		        PlatformConfigFile => ProjPath & "flow/PlatformConfig.json",
		        InboundLogFilename => ProjPath & "log/InLog" & integer'image(i) & ".txt",
		        OutboundLogFilename => ProjPath & "log/OutLog" & integer'image(i) & ".txt"
			)
			port map(
				Reset => reset,

				-- Output Interface (to Crossbar)
				ClockTx => PEInterfaces(i).ClockTx,
				Tx => PEInterfaces(i).Tx,
				DataOut => PEInterfaces(i).DataOut,
				CreditI => PEInterfaces(i).CreditI,

				-- Input Interface (from Crossbar)
				ClockRx => PEInterfaces(i).ClockRx,
				Rx => PEInterfaces(i).Rx,
				DataIn => PEInterfaces(i).DataIn,
				CreditO => PEInterfaces(i).CreditO
			);
		
	end generate PEGen;


	CrossbarGen: entity work.Crossbar

		generic map(
			Arbiter => "RR",
			AmountOfPEs => AmountOfPEs,
			PEAddresses => PEAddresses,
			BridgeBufferSize => 512,
			IsStandalone => true
		)
		port map(
			Clock => clock,
			Reset => reset,
			PEInterfaces => PEInterfaces
		);
	
end architecture RTL;