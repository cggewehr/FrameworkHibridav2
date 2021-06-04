--------------------------------------------------------------------------------
-- Title       : Crossbar interface module for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : CrossbarBridgev2.vhd
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


entity CrossbarBridge is

	generic(
		BufferSize : integer;
		AmountOfPEs: integer;
		PEAddresses: HalfDataWidth_vector;
        SelfIndex: integer;
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
		CreditI  : in std_logic;

		-- Arbiters Interface
		ACK      : out std_logic;
		Request  : out std_logic_vector;
		Grant    : in std_logic

	);
	
end entity CrossbarBridge;


architecture RTL of CrossbarBridge is

    type state_t is (Sstandby, Srequest, SwaitForGrant, StransmitHeader, StransmitSize, StransmitPayload);
	signal currentState: state_t;

    signal flitCounter: unsigned(DataWidth - 1 downto 0);
	signal targetIndex: integer range 0 to PEAddresses'high; 

    signal bufferDataOut: DataWidth_t;
	signal bufferAVFlag: std_logic;
	signal bufferReadConfirm: std_logic;
    signal bufferReadyFlag: std_logic;

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

		return Addresses'high;  -- Return index of wrapper if given ADDR was not found in crossbar
		
	end function GetIndexOfAddr;

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
			DataOut             => bufferDataOut,
			ReadConfirm         => bufferReadConfirm,
			ReadACK             => open,
			
			-- Status flags
			BufferEmptyFlag     => open,
			BufferFullFlag      => open,
			BufferReadyFlag     => CreditO,
			BufferAvailableFlag => bufferAVFlag

		);
    
    ClockTx <= Clock;
	Tx <= bufferAVFlag when currentState = StransmitHeader or currentState = StransmitSize or currentState = StransmitPayload else '0';
    DataOut <= bufferDataOut;
	bufferReadConfirm <= CreditI when currentState = StransmitHeader or currentState = StransmitSize or currentState = StransmitPayload else '0';
    
    -- Makes requests to self impossible
    Request(SelfIndex) <= '0';

	ControlFSM: process(Clock, Reset) begin

        if Reset = '1' then

            -- Set default values
            ACK <='0';
			Request <= (others => '0');

            flitCounter <= to_unsigned(0, DataWidth);

            currentState <= Sstandby;

        elsif rising_edge(Clock) then

		    case currentState is

			    -- Wait for a new message to be sent
			    when Sstandby =>

                    ACK <= '0';
                    Request <= (others => '0');

				    if bufferAVFlag = '1' then

                        --assert false report "targetIndex = <" & integer'image(GetIndexOfAddr(PEAddresses, DataIn(DataWidth - 1 downto HalfDataWidth), SelfIndex)) & "> for PEPos <" & integer'image(PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), 5)) & ">" severity note;
                        targetIndex <= GetIndexOfAddr(PEAddresses, bufferDataOut(DataWidth - 1 downto HalfDataWidth), SelfIndex);

					    currentState <= Srequest;

				    else
					    currentState <= Sstandby;

                    end if;

                -- Asserts "Request" to arbiter defined by targetIndex
                when Srequest =>

                    Request(targetIndex) <= '1';

                    assert targetIndex /= selfIndex report "Crossbar bridge <" & integer'image(selfIndex) & "> trying to transmit to itself" severity error;

                    currentState <= SwaitForGrant;

			    -- Waits for arbiter grant
			    when SwaitForGrant => 

                    if Grant = '1' then

					    Request(targetIndex) <= '0';

					    currentState <= StransmitHeader;

				    else
					    currentState <= SwaitForGrant;

				    end if;

                -- Transmit ADDR header flit through crossbar
                when StransmitHeader =>
                    
                    if CreditI = '1' and bufferAVFlag = '1' then
                        currentState <= StransmitSize;
                    else
                        currentState <= StransmitHeader;
                    end if;

                -- Transmit SIZE header flit through crossbar, and captures payload size to to count down from to time arbiter ACK signal
                when StransmitSize => 

                    flitCounter <= unsigned(bufferDataOut);

                    if CreditI = '1' and bufferAVFlag = '1' then
                        currentState <= StransmitPayload;
                    else
                        currentState <= StransmitSize;
                    end if;

				-- Transmits payload through crossbar
			    when StransmitPayload => 

				    if CreditI = '1' and bufferAVFlag = '1' then
					    flitCounter <= flitCounter - 1;
				    end if;

					-- Determines if this is the last flit of msg, frees arbiter if so
				    if flitCounter = 1 and CreditI = '1' and bufferAVFlag = '1' then
					    ACK <= '1';
					    currentState <= Sstandby;

				    else
					    currentState <= StransmitPayload;

				    end if;

		    end case;

		end if;

	end process ControlFSM;

	-- Debug assertions
	--assert not (Grant = '1' and currentState = Sstandby)
		--report "Unexpected grant at bridge " & integer'image(SelfIndex) severity ERROR;

	--assert not (currentState = Sstandby and bufferAVFlag = '1')
		--report "Buffer not empty at standby state in bridge " & integer'image(SelfIndex) severity ERROR;
	
end architecture RTL;
