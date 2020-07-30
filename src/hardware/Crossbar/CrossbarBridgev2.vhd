
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;


entity CrossbarBridge is

	generic(
		BufferSize : integer;
		AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector;
		SelfAddress: HalfDataWidth_t
	);
	port(

		-- Basic
		Clock    : in std_logic;
		Reset    : in std_logic;

		-- PE Interface
		ClockRx  : in std_logic;
		Rx       : in std_logic;
		DataIn   : in DataWidth_t;
		CreditO  : out std_logic;

		-- Crossbar Interface
		ClockTx  : out std_logic;
		Tx       : out std_logic;
		DataOut  : out DataWidth_t;
		CreditI  : in std_logic_vector;

		-- Arbiters Interface
		Ack      : out std_logic_vector;
		Request  : out std_logic_vector;
		Grant    : in std_logic_vector

	);
	
end entity CrossbarBridge;


architecture RTL of CrossbarBridge is

	type state_t is (Sreset, Sstandby, Srequest, SwaitForGrant, Stransmit);
	signal currentState: state_t;

    signal flitCounter: integer;
	signal targetIndex: integer; 

	signal bufferAVFlag: std_logic;
	signal bufferReadConfirm: std_logic;

	-- Searches through a given list of addresses of PEs contained in this crossbar, and returns index of a given address in given list of addresses,
    -- which matches the MUX selector value which produces the data value associated with the given address
	function GetIndexOfAddr(Addresses: HalfDataWidth_vector; AddressOfInterest: HalfDataWidth_t; IndexToSkip: integer) return integer is begin

		for i in 0 to Addresses'high - 1 loop  -- Ignores wrapper (Last element of Addresses[])

			if i = IndexToSkip then
				next;

			elsif Addresses(i) = AddressOfInterest then
				return i;

			end if;

		end loop;

		return 0;  -- Return index of wrapper if given ADDR was not found in crossbar
		
	end function GetIndexOfAddr;

	constant selfIndex: integer := GetIndexOfAddr(PEAddresses, SelfAddress, 0);

begin

	-- Instantiates a bisynchronous FIFO
	FIFO: entity work.CircularBuffer

		generic map (
			BufferSize => BufferSize,
			DataWidth  => DataWidth
		)
		port map (
			
			-- Basic
			Reset               => Reset,

			-- PE Interface (Input)
			ClockIn             => ClockRx,
			DataIn              => DataIn,
			DataInAV            => Rx,
			WriteACK            => open,

			-- Crossbar interface (Output)
			ClockOut            => Clock,
			DataOut             => DataOut,
			ReadConfirm         => bufferReadConfirm,
			ReadACK             => open,
			
			-- Status flags
			BufferEmptyFlag     => open,
			BufferFullFlag      => open,
			BufferReadyFlag     => CreditO,
			BufferAvailableFlag => bufferAVFlag

		);


	Tx <= bufferAVFlag when currentState = Stransmit else '0';


	bufferReadConfirm <= CreditI(targetIndex) when currentState = Stransmit else '0';


	ControlFSM: process(Clock) begin

		case currentState is

			-- Set default values
			when Sreset =>

				Ack <= (others => '0');
				Request <= (others => '0');

			-- Wait for a new message to be sent
			when Sstandby =>

				if Rx = '1' then

					targetIndex <= GetIndexOfAddr(PEAddresses, SelfAddress, selfIndex);

					currentState <= Srequest;

				else

					currentState <= Sstandby;

				end if;

			-- Requests to the right arbiter 
			when Srequest => 

				Request(targetIndex) <= '1';
				flitCounter <= to_integer(unsigned(DataIn)) + 2;

				currentState <= SwaitForGrant;

			-- Waits for arbiter grant
			when SwaitForGrant => 

				if Grant(targetIndex) = '1' then

					Ack(targetIndex) <= '1';
					Request(targetIndex) <= '0';

					currentState <= Stransmit;

				else

					currentState <= SwaitForGrant;

				end if;

			-- Sends message
			when Stransmit => 

				Ack(targetIndex) <= '0';

				if CreditI(targetIndex) = '1' and bufferAVFlag = '1' then
					flitCounter <= flitCounter - 1;

				end if;

				if flitCounter = 1 and CreditI(targetIndex) = '1' and bufferAVFlag = '1' then
					currentState <= Sstandby;

				else
					currentState <= Stransmit;

				end if;

			-- Defaults to Sreset;
			when others => 

				currentState <= Sreset;

		end case;


		if Reset = '1' then
			currentState <= Sreset;

		end if;

	end process ControlFSM;

	-- Debug assertions
	assert (to_integer(unsigned(Grant)) > 0 and (currentState = SwaitForGrant or currentState = Stransmit)) 
		report "Unexpected grant at bridge " & integer'image(selfIndex) severity ERROR;

	assert (currentState = Sstandby and bufferAVFlag = '0')
		report "Buffer not empty at standby state in bridge " & integer'image(selfIndex) severity ERROR;
	
end architecture RTL;
