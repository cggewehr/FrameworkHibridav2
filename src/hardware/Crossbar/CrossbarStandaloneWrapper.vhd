
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;


entity CrossbarStandaloneWrapper is

	generic(
		AmountOfPEs: integer;
		BridgeBufferSize: integer
	);
	port(
		Clock: std_logic;
		Reset: std_logic;
		PEInputs: out PEInputs_vector(0 to AmountOfPEs - 1);
		PEOutputs: in PEOutputs_vector(0 to AmountOfPEs - 1)
	);
	
end entity CrossbarStandaloneWrapper;


architecture RTL of CrossbarStandaloneWrapper is

begin

	StandaloneCrossbar: entity work.Crossbar

		generic map(
			ArbiterType => "RR",
			AmountOfPEs => AmountOfPEs,
			PEAddresses => GetDefaultPEAddresses(AmountOfPEs),
			BridgeBufferSize => BridgeBufferSize,
			IsStandalone => True
		)
		port map(
			Clock => Clock,
			Reset => Reset,
			PEInputs => PEInputs,
			PEOutputs => PEOutputs
		);
	
end architecture RTL;
