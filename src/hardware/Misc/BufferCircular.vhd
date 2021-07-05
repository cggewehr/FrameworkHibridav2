--------------------------------------------------------------------------------
-- Title       : Bisynchronous FIFO for clock domain crossing
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : BufferCircular.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : FIFO that will be written to at a given clock speed and read 
--              from at another
--               (Used protocol is ready-then-valid, meaning the producer entity
--              must handle flow control through the available status flags
--              and the WriteACK signal)
--------------------------------------------------------------------------------
-- Revisions   : v1.0 - Verified
--             : v1.1 - Flags set asynchronously and N + 1 bit regs to store pointers
--------------------------------------------------------------------------------
-- TODO        : Verification asserts
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.std_logic_unsigned.all;
    use ieee.numeric_std.all;
    use ieee.math_real.log2;
    use ieee.math_real.ceil;

entity CircularBuffer is

	generic (
		BufferSize : integer;
		DataWidth  : integer
	);
	port (

		-- Basic
		Reset               : in std_logic;

		-- Input Interface
		ClockIn             : in std_logic;
		DataIn              : in std_logic_vector(DataWidth - 1 downto 0);
		DataInAV            : in std_logic;
		WriteACK            : out std_logic;

		-- Output interface
		ClockOut            : in std_logic;
		DataOut             : out std_logic_vector(DataWidth - 1 downto 0);
		ReadConfirm         : in std_logic;
		ReadACK             : out std_logic;
		
		-- Status flags
		BufferEmptyFlag     : out std_logic;
		BufferFullFlag      : out std_logic;
		BufferReadyFlag     : out std_logic;
		BufferAvailableFlag : out std_logic

	);

end entity CircularBuffer;

architecture RTL of CircularBuffer is

    -- The buffer itself, where data is stored to and read from
	type bufferArray_t is array(natural range <>) of std_logic_vector(DataWidth - 1 downto 0);
	signal bufferArray: bufferArray_t(BufferSize - 1 downto 0);

    -- Pointers signaling what buffer slot is data to be read from/written to
    constant PointerSize: integer := integer(ceil(log2(real(BufferSize)))) + 1;
	signal readPointerReg: unsigned(PointerSize - 1 downto 0);
	signal writePointerReg: unsigned(PointerSize - 1 downto 0);
	signal readPointer: integer range 0 to BufferSize - 1;
	signal writePointer: integer range 0 to BufferSize - 1;

    -- Counter for how many buffer slots have been filled (Status flags are based on this value) 
    signal dataCount: integer range 0 to BufferSize;

begin

    -- Converts unsigned pointers - MSB to integers, which actually index the memory array
    readPointer <= to_integer(readPointerReg(readPointerReg'high - 1 downto 0));
    writePointer <= to_integer(writePointerReg(writePointerReg'high - 1 downto 0));

    -- Sets flags asynchronously
    dataCount <= to_integer(writePointerReg - readPointerReg);
	BufferEmptyFlag <= '1' when dataCount = 0 else '0';
	BufferFullFlag <= '1' when dataCount = BufferSize else '0';
	BufferReadyFlag <= '1' when dataCount /= BufferSize else '0';
	BufferAvailableFlag <= '1' when dataCount /= 0 else '0';

	-- Handles write requests 
	WriteProcess: process(ClockIn, Reset) begin

		if Reset = '1' then

			writePointerReg <= (others => '0');
			WriteACK <= '0';

		elsif rising_edge(ClockIn) then

			-- WriteACK is defaulted to '0'
			WriteACK <= '0';

			--   Checks for a write request. If there is valid data available and 
            -- free space on the buffer, write it and send ACK signal to producer entity
			if DataInAV = '1' and dataCount /= BufferSize then

				bufferArray(writePointer) <= DataIn;
				writePointerReg <= writePointerReg + 1;

				WriteACK <= '1';

			end if;

		end if;

	end process;

    -- Asynchronously reads from buffer (FWFT) (Synchronously increments pointer, below)
    DataOut <= bufferArray(readPointer);

	-- Handles read events
	ReadProcess: process(ClockOut, Reset) begin

		if Reset = '1' then

			readPointerReg <= (others => '0');
            ReadACK <= '0';

		elsif rising_edge(ClockOut) then

            ReadACK <= '0';

			-- Checks for a read event. If there is data on the buffer, pass in on to consumer entity
			if ReadConfirm = '1' and dataCount /= 0 then
    
                ReadACK <= '1';
				readPointerReg <= readPointerReg + 1;

			end if;

		end if;

	end process;

end architecture RTL;
