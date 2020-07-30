--------------------------------------------------------------------------------
-- Title       : Bus interface module for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : BusBridgev2.vhd
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

library work;
	use work.HyHeMPS_PKG.all;


entity BusBridge is

	generic(
		BufferSize : integer
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

		-- Bus Interface
		ClockTx  : out std_logic;
		Tx       : out std_logic;
		DataOut  : out DataWidth_t;
		CreditI  : in std_logic;

		-- Arbiter Interface
		Ack      : out std_logic;
		Request  : out std_logic;
		Grant    : in std_logic

	);

end BusBridge;


architecture RTL of BusBridge is

	type state_t is (Sreset, Sstandby, SwaitForGrant, Stransmit);
	signal currentState: state_t;
	
	signal flitCounter: integer;

	signal dataTristate: DataWidth_t;

	signal bufferAVFlag: std_logic;

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

			-- Bus interface (Output)
			ClockOut            => Clock,
			DataOut             => dataTristate,
			ReadConfirm         => CreditI,
			ReadACK             => open,
			
			-- Status flags
			BufferEmptyFlag     => open,
			BufferFullFlag      => open,
			BufferReadyFlag     => CreditO,
			BufferAvailableFlag => bufferAVFlag

		);


	-- 
	ClockTx <= Clock;


	-- 
	Tx <= bufferAVFlag when currentState = Stransmit else 'Z';


	-- 
	DataOut <= dataTristate when currentState = Stransmit else (others => 'Z');


	-- 
	ControlFSM: process(Clock) begin

		if rising_edge(Clock) then

			case currentState is

				-- Sets default values
				when Sreset => 

					Ack <= 'Z';
					Request <= '0';

				-- Waits for a new message
				when Sstandby => 

					if Rx = '1' then

						Request <= '1';

						currentState <= SwaitForGrant;

					else
						currentState <= Sstandby;

					end if;

				-- Waits for arbiter grant signal
				when SwaitForGrant => 

					flitCounter <= to_integer(unsigned(DataIn)) + 2;

					if Grant = '1' then

						Ack <= '1';
						Request <= '0';

						currentState <= Stransmit;

					else

						currentState <= SwaitForGrant;

					end if;

				-- Transmits message through bus
				when Stransmit => 

					Ack <= 'Z';

					if CreditI = '1' then
						flitCounter <= flitCounter - 1;

					end if;

					-- Determines if this is the last flit of msg
					if flitCounter = 1 and CreditI = '1' then
						currentState <= Sstandby;

					else
						currentState <= Stransmit;

					end if;

			end case;

			if Reset = '1' then

				currentState <= Sreset;

			end if;

		end if;

	end process ControlFSM;
	
end architecture RTL;
