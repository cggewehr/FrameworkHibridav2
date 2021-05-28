--------------------------------------------------------------------------------
-- Title       : Receiver
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : Receiver.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description: 
--------------------------------------------------------------------------------
-- TODO:
--------------------------------------------------------------------------------

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library std;
    use std.textio.all;

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;
    use HyHeMPS.Injector_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;


entity Logger is

	generic(
		InboundLogFilename : string;
		OutboundLogFilename : string;
		SquareNoCBound: integer
	);

	port (

        -- Basic
        --Clock   : in std_logic;
        Reset   : in std_logic;

        -- Output Interface (to network)
        ClockTx : in std_logic;
        Tx      : in std_logic;
        DataOut : in DataWidth_t;
        CreditI : in std_logic;

        -- Input Interface (from network)
        ClockRx : in std_logic;        
        Rx      : in std_logic;
        DataIn  : in DataWidth_t;
        CreditO : in std_logic

	);
	
end entity Logger;


architecture RTL of Logger is

    -- Assumes header = [ADDR, SIZE]
    constant HeaderSize: integer := 2;

    -- Service IDs
    constant DVFSServiceID: DataWidth_t := "0000FFFF";
    constant SyntheticTrafficServiceID: DataWidth_t := "FFFF0000";

    -- Opens log files
    file InboundLog: text open write_mode is InboundLogFilename;
    file OutboundLog: text open write_mode is OutboundLogFilename;

begin

	InputLogger: process(ClockRx, Reset)

        variable flitCounter: integer := 0;
        variable payloadSize: integer := 0;
        variable service: DataWidth_t := (others => '0');
        variable serviceGo: boolean := False;

        variable inputTimestamp: integer := 0;
        variable checksum: integer := 0;

        variable inboundLogLine: line;

    begin

        if Reset = '1' then

            flitCounter := 0;
            payloadSize := 0;
            serviceGo := False;

            inputTimestamp := 0;
            checksum := 0;

        elsif rising_edge(ClockTx) then

            if Rx = '1' and CreditO = '1' then

                -- Write to log ADDR flit
                if flitCounter = 0 then

                    write(inboundLogLine, integer'image(PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), SquareNoCBound)) & " ");

                -- Write to log SIZE flit
                elsif flitCounter = 1 then

                    payloadSize := to_integer(unsigned(DataIn));
                    write(inboundLogLine, integer'image(to_integer(unsigned(DataIn))) & " ");

                -- Write to log ServiceID flit
                elsif flitCounter = 2 then

                    write(inboundLogLine, CONV_STRING(DataIn) & " ");
                    service := DataIn;
                    serviceGo := True;

                end if;

                -- Decodes message payload flits according to ServiceID
                if serviceGo then

                    if service = DVFSServiceID then

                        if flitCounter = 3 then

                            -- Write DVFS config filt
                            write(inboundLogLine, CONV_STRING(DataIn) & " ");

                        end if;

                    elsif service = SyntheticTrafficServiceID then


                        if flitCounter = 3 then

                            -- Write App ID
                            write(inboundLogLine, integer'image(to_integer(unsigned(DataIn) & " ")));

                        elsif flitCounter = 4 then

                            -- Write Target Thread ID
                            write(inboundLogLine, integer'image(to_integer(unsigned(DataIn) & " ")));

                        elsif flitCounter = 5 then

                            -- Write Source Thread ID
                            write(inboundLogLine, integer'image(to_integer(unsigned(DataIn) & " ")));

                        end if;

                    -- OTHER SERVICE DECODING LOGIC GOES HERE -- 

                    else

                        report "Service ID <" & CONV_STRING(service) & "> unrecognized" severity warning; 

                    end if;

                end if; 

                -- Update Checksum with new flit
                checksum := checksum + to_integer(unsigned(DataIn));

                -- Increments counter if its less than current message size or SIZE flit has not yet been sent
                if (flitCounter < payloadSize + HeaderSize - 1) or (flitCounter < HeaderSize) then

                    flitCounter := flitCounter + 1;

                -- Whole message has been sent, increments message counter and reset flit counter
                else

                    -- Write to log file (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
                    inputTimestamp := NOW / 1 ns;
                    write(inboundLogLine, integer'image(inputTimestamp) & " ");
                    write(inboundLogLine, integer'image(checksum));
                    writeline(inboundLog, inboundLogLine);

                    -- Resets flags and counters
                    flitCounter := 0;
                    payloadSize := 0;
                    serviceGo := False;
                    checksum := 0;
                    inputTimestamp := 0;

                end if;

            end if;

        end if;

    end process;


    OutputLogger: process(ClockTx, Reset) 

        variable flitCounter: integer := 0;
        variable payloadSize: integer := 0;
        variable service: DataWidth_t := (others => '0');
        variable serviceGo: boolean := False;

        variable outputTimestamp: integer := 0;
        variable checksum: integer := 0;

        variable outboundLogLine: line;
        
    begin

        if Reset = '1' then

            flitCounter := 0;
            payloadSize := 0;
            serviceGo := False;

            outputTimestamp := 0;
            checksum := 0;

        elsif rising_edge(ClockTx) then

            if Tx = '1' and CreditI = '1' then

                -- Write to log ADDR flit
                if flitCounter = 0 then

                    outputTimestamp := NOW / 1 ns;
                    write(outboundLogLine, integer'image(PEPosFromXY(DataOut(DataWidth - 1 downto HalfDataWidth), SquareNoCBound)) & " ");

                -- Write to log SIZE flit
                elsif flitCounter = 1 then

                    payloadSize := to_integer(unsigned(DataOut));
                    write(outboundLogLine, integer'image(to_integer(unsigned(DataOut))) & " ");

                -- Write to log ServiceID flit
                elsif flitCounter = 2 then

                    write(outboundLogLine, CONV_STRING(DataOut) & " ");
                    service := DataOut;
                    serviceGo := True;

                end if;

                -- Decodes message payload flits according to ServiceID
                if serviceGo then

                    if service = DVFSServiceID then

                        if flitCounter = 3 then

                            -- Write DVFS config filt
                            write(outboundLogLine, CONV_STRING(DataOut) & " ");

                        end if;

                    elsif service = SyntheticTrafficServiceID then


                        if flitCounter = 3 then

                            -- Write App ID
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut) & " ")));

                        elsif flitCounter = 4 then

                            -- Write Target Thread ID
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut) & " ")));

                        elsif flitCounter = 5 then

                            -- Write Source Thread ID
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut) & " ")));

                        end if;

                    -- OTHER SERVICE DECODING LOGIC GOES HERE -- 

                    else

                        report "Service ID <" & CONV_STRING(service) & "> unrecognized" severity warning; 

                    end if;

                end if; 

                -- Update Checksum with new flit
                checksum := checksum + to_integer(unsigned(DataOut));

                -- Increments counter if its less than current message size or SIZE flit has not yet been sent
                if (flitCounter < payloadSize + HeaderSize - 1) or (flitCounter < HeaderSize) then

                    flitCounter := flitCounter + 1;

                -- Whole message has been sent, increments message counter and reset flit counter
                else

                    -- Write to log file (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
                    write(outboundLogLine, integer'image(outputTimestamp) & " ");
                    write(outboundLogLine, integer'image(checksum));
                    writeline(outboundLog, outboundLogLine);

                    -- Resets flags and counters
                    flitCounter := 0;
                    payloadSize := 0;
                    serviceGo := False;
                    checksum := 0;
                    outputTimestamp := 0;

                end if;

            end if;

        end if;

    end process;
	
end architecture RTL;
