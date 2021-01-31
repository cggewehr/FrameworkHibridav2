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


entity InjBuffer is

	generic(
		BufferSize : integer
	);
	port(

		-- Basic
		Clock   : in std_logic;
		Reset   : in std_logic;

		-- Injector Interface
		ClockRx : in std_logic;
		Rx      : in std_logic;
		DataIn  : in DataWidth_t;
		CreditO : out std_logic;

		-- Bus Interface
		ClockTx : out std_logic;
		Tx      : out std_logic;
		DataOut : out DataWidth_t;
		CreditI : in std_logic;

		-- Arbiter Interface
		ACK     : out std_logic;
		Request : out std_logic;
		Grant   : in std_logic

	);

end InjBuffer;


architecture RTL of InjBuffer is

	type rxState_t is (Sreset, Sstandby, Ssize, Sfill, SwaitForGrant, Stransmit);
	signal rxState: rxState_t;

	type txState_t is (Sreset, Sstandby, Stransmit);
	signal txState: txState_t;
	
	signal rxCounter: unsigned(DataWidth - 1 downto 0);
	signal txCounter: unsigned(DataWidth - 1 downto 0);

	signal txEnable: std_logic;

	signal FIFODataOut: DataWidth_t;
	signal FIFODataCount: integer;
	signal FIFOAVFlag: std_logic;
	signal FIFOReadyFlag: std_logic;

begin

	-- Instantiates a bisynchronous FIFO
	FIFO: entity work.CircularBuffer

		generic map(
			BufferSize => BufferSize,
			DataWidth  => DataWidth
		)
		port map(
			
			-- Basic
			Reset               => Reset,

			-- PE Interface (Input)
			ClockIn             => ClockRx,
			DataIn              => DataIn,
			DataInAV            => Rx,
			WriteACK            => open,

			-- Bus interface (Output)
			ClockOut            => Clock,
			DataOut             => FIFODataOut,
			ReadConfirm         => CreditI,
			ReadACK             => open,
			
			-- Status flags
			--DataCount           => FIFODataCount,
			BufferEmptyFlag     => open,
			BufferFullFlag      => open,
			--BufferReadyFlag     => CreditO,
			BufferReadyFlag     => FIFOReadyFlag,
			BufferAvailableFlag => FIFOAVFlag

		);


	-- 
	ClockTx <= Clock;


	-- 
	--Tx <= bufferAVFlag when currentState = Stransmit else 'Z';
	--Tx <= FIFOAVFlag when currentState = Stransmit else 'Z';
	--Tx <= FIFOAVFlag when FIFODataCount > 0 and txEnable = '1' else 'Z';
	Tx <= FIFOAVFlag when txEnable = '1' else 'Z';


	-- 
	--DataOut <= dataTristate when currentState = Stransmit else (others => 'Z');
	--DataOut <= FIFODataOut when currentState = Stransmit else (others => 'Z');
	--DataOut <= FIFODataOut when FIFODataCount > 0 and txEnable = '1' else (others => 'Z');
	DataOut <= FIFODataOut when txEnable = '1' else (others => 'Z');


	-- 
	--CreditO <= '0' when currentState = Stransmit or currentState = SwaitForGrant else bufferReadyFlag;
	CreditO <= FIFOReadyFlag;
	--injSideCreditI <= '0' when currentState = Stransmit or currentState = SwaitForGrant else structSideReadyFlag;


	-- 
	RxFSM: process(ClockRx, Reset) begin

		if Reset = '1' then
			rxState <= Sreset;

		elsif rising_edge(ClockRx) then

			case rxState is

				-- Sets default values
				when Sreset => 

					rxCounter <= (others => '0');
					txCounter <= (others => '0');

					txEnable <= '0';

					ACK <= 'Z';
					Request <= '0';

					rxState <= Sstandby;

				-- Waits for a new message
				when Sstandby => 

					ACK <= 'Z';

					-- New message with ADDR flit @ data in
					if Rx = '1' and FIFOReadyFlag = '1' then
					--if structSideReadyFlag = '1' and injSideAVFlag = '1' then
						rxState <= Ssize;

					else
						rxState <= Sstandby;

					end if;

				-- Captures message size
				when Ssize => 

					--if Rx = '1' and bufferReadyFlag = '1' then
					if Rx = '1' and FIFOReadyFlag = '1' then

						rxCounter <= unsigned(DataIn);
						txCounter <= unsigned(DataIn) + 2;

						rxState <= Sfill;

					else
						rxState <= Ssize;
					end if;

				-- Fills buffer with payload
				when Sfill => 

					if Rx = '1' and FIFOReadyFlag = '1' then
					--if structSideReadyFlag = '1' and injSideAVFlag = '1' then
						rxCounter <= rxCounter - 1;
					end if;

					-- Done filling buffer, ready to transmit
					if rxCounter = 1 then
						Request <= '1';
						rxState <= SwaitForGrant;
					else
						rxState <= Sfill;
					end if;

				-- Waits for arbiter grant signal
				when SwaitForGrant => 

					if Grant = '1' then

						ACK <= '0';
						Request <= '0';

						txEnable <= '1';

						rxState <= Stransmit;

					else
						rxState <= SwaitForGrant;

					end if;

				-- Transmits message through bus
				when Stransmit => 

					--if CreditI = '1' then
					--	flitCounter <= flitCounter - 1;

					--end if;

					-- Frees bus if done transmiting
					--if flitCounter = 1 and CreditI = '1' then
					--if FIFODataCount = 0 then
					--	currentState <= Sstandby;
					--	ACK <= '1';

					--else
					--	currentState <= Stransmit;

					--end if;

					if txEnable = '0' then

						ACK <= '1';

						rxState <= Sstandby;

					else
						rxState <= Stransmit;
					end if;

			end case;

		end if;

	end process RxFSM;


	TxFSM: process(Clock, Reset) begin

		if Reset = '1' then
			txState <= Sreset;

		elsif rising_edge(Clock) then

			case txState is

				when Sreset =>
					txState <= Sstandby;
					
				-- TODO: This state is not really needed, it should be merged into Stransmit with an additional "txEnable = '1'" check in addition to CreditI and FIFOAVFlag
				when Sstandby =>

					if txEnable = '1' then
						txState <= Stransmit;
					else
						txState <= Sstandby;
					end if;
				
				when Stransmit => 

					if CreditI = '1' and FIFOAVFlag = '1' then

						txCounter <= txCounter - 1;

						if txCounter = 1 then

							ACK <= '1';
							txEnable  <= '0';

							txState <= Sstandby;

						end if;

					else
						txState <= Stransmit;
					end if;

			end case;

		end if;


	end process TxFSM;
	
end architecture RTL;
