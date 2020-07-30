--------------------------------------------------------------------------------
-- Title       : <Title Block>
-- Project     : Default Project Name
--------------------------------------------------------------------------------
-- File        : Receiver.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Copyright (c) 2020 User Company Name
-------------------------------------------------------------------------------
-- Description: 
--------------------------------------------------------------------------------
-- Revisions:  Revisions and documentation are controlled by
-- the revision control system (RCS).  The RCS should be consulted
-- on revision history.
-------------------------------------------------------------------------------


library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all;

library std;
    use std.textio.all;


entity Receiver is

	generic(
		InboundLogFilename : string
	);

	port (
		Clock : in std_logic;
		Reset : in std_logic;

		-- Input Buffer Interface
		DataIn: in DataWidth_t;
		Rx: in std_logic;
		CreditO: out std_logic
	);
	
end entity Receiver;


architecture RTL of Receiver is

    constant HeaderSize: integer := 2;

	signal messageCounter: integer := 0;
    signal flitCounter: integer := 0;
    
    signal targetID: integer := 0;
    signal payloadSize: integer := 0;
    signal sourceID: integer := 0;
    signal outputTimestamp: integer := 0;

    file InboundLog: text open write_mode is InboundLogFilename;

begin

	-- Assumes header = [ADDR, SIZE]
	ReceiverProcess: process(Clock, Reset)
        variable InboundLogLine: line;
    begin

        -- Read request signal will always be set to '1' unless Reset = '1'
        CreditO <= '1';

        if Reset = '1' then

            -- Set default values and disables buffer read request
            CreditO <= '0';
            flitCounter <= 0;
            messageCounter <= 0;

        elsif rising_edge(Clock) then
            
            -- Checks for a new flit available on input buffer
            if Rx = '1' then

                -- Checks for an ADDR flit (Assumes header = [ADDR, SIZE])
                if flitCounter = 0 then

                    --latestMessageTimestamp <= std_logic_vector(to_unsigned(clockCounter, DataWidth));
                    targetID <= to_integer(unsigned(DataIn));
                    --null;

                -- Checks for a SIZE flit (Assumes header = [ADDR, SIZE])
                elsif flitCounter = 1 then

                    payloadSize <= to_integer(unsigned(DataIn));

                -- Saves source ID (Assumes first payload flit containts PEPOS of sender)
                elsif flitCounter = 2 then

                    sourceID <= to_integer(unsigned(DataIn));

                elsif flitCounter = 3 then

                    outputTimestamp <= to_integer(unsigned(DataIn));

                end if;

                -- Increments counter if its less than current message size or SIZE flit has not yet been received
                -- "HeaderSize" is read from injector JSON config
                --if (flitCounter < currentPayloadSize) or (flitCounter < HeaderSize) then
                if (flitCounter < payloadSize + HeaderSize - 1) or (flitCounter < HeaderSize) then

                    flitCounter <= flitCounter + 1;

                -- Whole message has been received, increments message counter and reset flit counter
                else

                    -- TODO: Find if received message fits an expected pattern, and if so, inform DPD injector

                    -- Write to log file ( | target ID | source ID | payload size | output timestamp | input timestamp | )
                    --write(InboundLogLine, integer'image(messageCounter) & " ");
                    write(InboundLogLine, integer'image(targetID) & " ");
                    write(InboundLogLine, integer'image(sourceID) & " ");
                    write(InboundLogLine, integer'image(payloadSize) & " ");
                    write(InboundLogLine, integer'image(outputTimestamp) & " ");
                    write(InboundLogLine, integer'image(now / 1 ns));
                    writeline(InboundLog, InboundLogLine);

                    -- Signals a message has been received to DPD injector and updates counters
                    messageCounter <= incr(messageCounter, 10000000, 0);
                    --semaphore <= incr(Semaphore, UINT32MaxValue, 0);
                    flitCounter <= 0;

                end if;

            end if;

        end if;

    end process;
	
end architecture RTL;
