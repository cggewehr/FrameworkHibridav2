
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library HyHeMPS;
	use HyHeMPS.HyHeMPS_PKG.all;


entity BusStandaloneWrapper is

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
	
end entity BusStandaloneWrapper;


architecture RTL of BusStandaloneWrapper is

begin

	StandaloneBus: entity work.HyBus

		generic map(
			Arbiter => "RR",
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
