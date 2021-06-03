
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;


entity ArbiterFactory is

	generic ( 
		ArbiterType: string(1 to 2);
		AmountOfPEs : integer
	);
	port (
		Clock : in std_logic;
		Reset : in std_logic;

		Req   : in std_logic_vector(0 to AmountOfPEs - 1);
		Ack   : in std_logic;
		Grant : out std_logic_vector(0 to AmountOfPEs - 1)
	);

end entity ArbiterFactory;


architecture Factory of ArbiterFactory is

	-- Defines suported arbiter types. Add new arbiter types here when implemented and instantiate them in the architecture body 
	constant AmountOfSupportedArbiters: integer := 1;
	type SupportedArbiters_t is array(0 to AmountOfSupportedArbiters - 1) of string(1 to 2);
	--constant SupportedArbiters: SupportedArbiters_t := ("RR");
	constant SupportedArbiters: SupportedArbiters_t := (0 => "RR");

	-- Checks if given arbiter type corresponds to an implemented arbiter architecture
	function assertArbiterType (ArbiterType: string(1 to 2); SupportedArbiters: SupportedArbiters_t) return boolean is 
		variable isSupported: boolean := false;
	begin
		
		for i in SupportedArbiters'range loop
			if SupportedArbiters(i) = ArbiterType then
				isSupported := True;
				exit;
			end if;
		end loop;

		return isSupported;

	end function assertArbiterType;

begin

	-- Checks if given arbiter type corresponds to an implemented arbiter archtecture
	assert assertArbiterType(ArbiterType, SupportedArbiters) report "Given ArbiterType <" & ArbiterType & "> not recognized" severity failure;

	-- Instantiates Round Robin arbiter
	RoundRobinGen: if ArbiterType = "RR" generate

		RoundRobinArbiter: entity work.RoundRobinArbiter

			generic map(
				AmountOfPEs => AmountOfPEs
			)
			port map(
				
				Clock => Clock,
				Reset => Reset,

				Req => Req,
				ACK => ACK,
				Grant => Grant

			);


	end generate RoundRobinGen;

	-- Instantiates Daisy Chain arbiter
	--DaisyChainGen: if ArbiterType = "DC" generate

    --    DaisyChainArbiter: entity work.DaisyChainArbiter

	--		generic map(
	--			AmountOfPEs => AmountOfPEs
	--		)
	--		port map(
		
	--			Clock => Clock,
	--			Reset => Reset,

	--			Req => Req,
	--			ACK => ACK,
	--			Grant => Grant

	--		);

	--end generate DaisyChainrGen;

end architecture Factory;