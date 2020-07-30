--------------------------------------------------------------------------------
-- Title       : Bisynchronous FIFO for clock domain crossing
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : BufferCircular.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : FIFO that get be written to at a given clock speed and read 
--              from at another
--------------------------------------------------------------------------------
-- Revisions   : v1.0 - Verified
--------------------------------------------------------------------------------
-- TODO        : Optimize and parametrize flags
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.std_logic_unsigned.all;

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
	signal readPointer: integer range 0 to BufferSize - 1;
	signal writePointer: integer range 0 to BufferSize - 1;

    -- Counter for how many buffer slots have been filled 
    --(Status flags are based on this value) 
	signal dataCount: integer range 0 to BufferSize;

    -- Gets set to '1' when first write after a reset occurs
    signal initialized: std_logic;

	-- Simple increment and wrap around
    --   (Used for resetting Read and Write pointers back to 0 (first buffer slot)
    -- once they've reached the end of the buffer)
	function incr(Value: integer ; MaxValue: in integer ; MinValue: in integer) return integer is

	begin

		if Value = MaxValue then
			return MinValue;
		else
			return Value + 1;
		end if;

	end function incr;

begin


    -- Update flags asynchronously, based on dataCount value
	BufferEmptyFlag <= '1' when dataCount = 0 else '0';
	BufferFullFlag <= '1' when dataCount = BufferSize else '0';
	BufferReadyFlag <= '1' when dataCount < BufferSize else '0';
	BufferAvailableFlag <= '1' when dataCount > 0 else '0';


    -- Update Data Count based on writePointer and readPointer values
    UpdateDataCount : process(Reset, writePointer, readPointer) 
        
        variable lastEventWasWrite : std_logic;

    begin

        -- Determines if last event was a either a Read or a Write
        --   (Necessary for when both pointer are equal, when so, amount of data
        -- on buffer can be determined by what event was the latest: if it was a
        -- write, it means that writePointer catched up to readPointer, implying
        -- that the next write on the buffer would overwrite the oldest buffer 
        -- slot, so, in conclusion, the buffer is full. Otherwise, if readPointer
        -- catched up to writePointer, all the available data on the buffer has 
        -- already been consumed)
        if Reset = '1' then

            dataCount <= 0;
            
        elsif writePointer'event then

            lastEventWasWrite := '1';

        elsif readPointer'event then

            lastEventWasWrite := '0';

        end if;

        -- Update dataCount value
        if writePointer > readPointer then
            dataCount <= writePointer - readPointer;
        elsif writePointer < readPointer then
            dataCount <= (writePointer + BufferSize) - readPointer;
        elsif writePointer = readPointer and lastEventWasWrite = '1' and initialized = '1' then
            dataCount <= BufferSize;
        elsif writePointer = readPointer and lastEventWasWrite = '0' and initialized = '1' then
            dataCount <= 0;
        else -- writePointer = readPointer and initialized = '0'
            dataCount <= 0;
        end if;

    end process UpdateDataCount;


	--   Handles write requests (Used protocol is ready-then-valid, meaning the
    -- producer entity must handle flow control through the available status flags
    -- and the WriteACK signal)
	WriteProcess : process(ClockIn, Reset) begin

		if Reset = '1' then

			writePointer <= 0;
			WriteACK <= '0';
            initialized <= '0';

		elsif rising_edge(ClockIn) then

			-- WriteACK is defaulted to '0'
			WriteACK <= '0';

			--   Checks for a write request. If there is valid data available and 
            -- free space on the buffer, write it and send ACK signal to producer entity
			if DataInAV = '1' and dataCount < bufferSize then

				bufferArray(writePointer) <= dataIn;
				WriteACK <= '1';
				writePointer <= incr(writePointer, bufferSize - 1, 0);
                initialized <= '1';

			end if;

		end if;

	end process;


    -- Asynchronously reads from buffer (Synchronously increments pointer)
    DataOut <= bufferArray(readPointer) when initialized = '1' else (others=>'0');


	-- Handles read events
	ReadProcess : process(ClockOut, Reset) begin

		if Reset = '1' then

			readPointer <= 0;
            ReadACK <= '0';

		elsif rising_edge(ClockOut) then

            ReadACK <= '0';

			-- Checks for a read event. If there is data on the buffer, pass in on to consumer entity
			if ReadConfirm = '1' and dataCount > 0 then
    
                ReadACK <= '1';
				readPointer <= incr(readPointer, BufferSize - 1, 0);

			end if;

		end if;

	end process;


end architecture RTL;
