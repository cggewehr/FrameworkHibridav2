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

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all; 


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
		ACK      : out std_logic;
		Request  : out std_logic;
		Grant    : in std_logic;

        -- Control Interface
        DisableInterrupt: out std_logic

	);

end BusBridge;


architecture RTL of BusBridge is

    --type state_t is (Sstandby, SwaitForGrant, StransmitHeader, StransmitSize, StransmitPayload);
    type state_t is (Sstandby, StransmitHeader, StransmitSize, StransmitPayload, SwaitForACK);
	signal currentState: state_t;
	
	signal flitCounter: unsigned(DataWidth - 1 downto 0);

	signal bufferDataOut: DataWidth_t;
	signal bufferAVFlag: std_logic;
    signal bufferReadConfirm: std_logic;

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
			DataOut             => bufferDataOut,
            ReadConfirm         => bufferReadConfirm,
			ReadACK             => open,
			
			-- Status flags
			BufferEmptyFlag     => open,
			BufferFullFlag      => open,
			BufferReadyFlag     => CreditO,
			BufferAvailableFlag => bufferAVFlag

		);

	-- Same as struct clock (clock domain crossing occurs at InjBuffer)
	ClockTx <= Clock;
	Tx <= bufferAVFlag when currentState /= SwaitForACK else '0';
	DataOut <= bufferDataOut;
    bufferReadConfirm <= CreditI when currentState = StransmitHeader or currentState = StransmitSize or currentState = StransmitPayload else '0';

    -- Only allows Bus to be interrupted when sending Payload flits, except for the last Flit
    --DisableInterrupt <= '1' when flitCounter = 1 else '0';
    DisableInterrupt <= '0' when currentState = StransmitPayload and flitCounter /= 1 else '1';

	ControlFSM: process(Clock, Reset) begin

        if Reset = '1' then

            -- Set default values
            ACK <= '0';
			Request <= '0';

            flitCounter <= to_unsigned(0, DataWidth);

			currentState <= Sstandby;

		elsif rising_edge(Clock) then

			case currentState is

				-- Waits for a new message
				when Sstandby => 
                    
                    ACK <= '0';
			        Request <= '0';

					if bufferAVFlag = '1' then

						Request <= '1';

						currentState <= StransmitHeader;

					else
						currentState <= Sstandby;
					end if;

				-- Waits for arbiter grant signal
				--when SwaitForGrant => 

					--if Grant = '1' then

						--Request <= '0';

						--currentState <= StransmitHeader;

					--else
					--	currentState <= SwaitForGrant;
					--end if;

                -- Transmit ADDR header flit through bus
                when StransmitHeader =>
                    
                    if Grant = '1' and CreditI = '1' and bufferAVFlag = '1' then
						Request <= '0';
                        currentState <= StransmitSize;
                    else
                        currentState <= StransmitHeader;
                    end if;

                -- Transmit SIZE header flit through bus, and captures payload size to to count down from to time arbiter ACK signal
                when StransmitSize => 

                    flitCounter <= unsigned(bufferDataOut);

                    if CreditI = '1' and bufferAVFlag = '1' then
                        currentState <= StransmitPayload;
                    else
                        currentState <= StransmitSize;
                    end if;

				-- Transmits payload through bus
				when StransmitPayload => 

					if CreditI = '1' and bufferAVFlag = '1' then
					    flitCounter <= flitCounter - 1;
				    end if;

					-- Determines if this is the last flit of msg, frees arbiter if so
					if flitCounter = 1 and CreditI = '1' and bufferAVFlag = '1' then
						ACK <= '1';
						--currentState <= Sstandby;
						currentState <= SwaitForACK;

					else
						currentState <= StransmitPayload;
					end if;

				-- Finishes packet transmission
				when SwaitForACK => 
				    currentState <= Sstandby;
				    ACK <= '0';
    
			end case;

		end if;

	end process ControlFSM;
	
end architecture RTL;
