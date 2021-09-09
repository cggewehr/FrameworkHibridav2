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
    
		SquareNoCBound: integer;

        -- For Bus interruption detection
        --CommStructure: string(1 to 3);
        AmountOfPEs: integer := 36;
        MaxMSGLength: integer := 128    
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
    constant DVFSServiceID: DataWidth_t := x"0000FFFF";
    constant SyntheticTrafficServiceID: DataWidth_t := x"FFFF0000";

    -- Opens log files
    file InboundLog: text open write_mode is InboundLogFilename;
    file OutboundLog: text open write_mode is OutboundLogFilename;

begin

	InputLogger: process(ClockRx, Reset)

        variable PEPos: integer := 0;

        variable flitCounter: integer := 0;
        variable payloadSize: integer := 0;
        variable service: DataWidth_t := (others => '0');
        variable serviceGo: boolean := False;

        variable inputTimestamp: integer := 0;
        variable checksum: unsigned(DataWidth - 1 downto 0) := (others =>'0');

        variable inboundLogLine: line;

        variable interrupted: boolean := False;
        variable interruptedInboundLogLine: line;

        variable interruptedInputTimestamp: integer := 0;
        variable interruptedChecksum: unsigned(DataWidth - 1 downto 0) := (others =>'0');

        variable interruptedFlitCounter: integer := 0;
        variable interruptedPayloadSize: integer := 0;
        variable interruptedService: DataWidth_t := (others => '0');
        variable interruptedServiceGo: boolean := False;

        -- 
        --procedure lineHelper(data: string; interrupted: boolean) is begin
        procedure lineHelper(data: string) is begin

            if interrupted then
                write(interruptedInboundLogLine, data & " ");
            else
                write(inboundLogLine, data & " ");
            end if;

        end procedure lineHelper;

    begin

        if Reset = '1' then

            PEPos := 0;

            flitCounter := 0;
            payloadSize := 0;
            service := (others => '0');
            serviceGo := False;

            inputTimestamp := 0;
            checksum := (others =>'0');

            interrupted := False;

            interruptedInputTimestamp := 0;
            interruptedChecksum := (others =>'0');

            interruptedflitCounter := 0;
            interruptedPayloadSize := 0;
            interruptedService := (others => '0');
            interruptedServiceGo := False;

        elsif rising_edge(ClockRx) then

            if Rx = '1' and CreditO = '1' then

                -- Check if new flit is the first (ADDR) flit from an interrupt
                --if PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), SquareNoCBound) < AmountOfPEs and to_integer(unsigned(DataIn)) > MaxMSGLength and DataIn /= DVFSServiceID and not interrupted and CommStructure = "Bus" and flitCounter > 0 then
                if PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), SquareNoCBound) < AmountOfPEs and to_integer(unsigned(DataIn)) > MaxMSGLength and DataIn /= DVFSServiceID and not interrupted and flitCounter > 0 then
                    
                    --report "DataIn: " & CONV_STRING(DataIn) severity note;
                    --assert not interrupted report "Logger interrupted while already interrupted" severity error;
                    --assert to_integer(unsigned(DataIn)) /= 126 report "Interrupt triggered by SIZE flit" severity error;
                    interrupted := True;

                    interruptedFlitCounter := flitCounter;
                    interruptedPayloadSize := payloadSize;
                    interruptedServiceGo := serviceGo;
                    interruptedChecksum := checksum;

                    flitCounter := 0;
                    payloadSize := 0;
                    serviceGo := False;
                    checksum := (others =>'0');
                     
                end if;

                -- Write to log line ADDR flit
                if flitCounter = 0 then

                    --write(inboundLogLine, integer'image(PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), SquareNoCBound)) & " ");
                    PEPos := PEPosFromXY(DataIn(DataWidth - 1 downto HalfDataWidth), SquareNoCBound);
                    lineHelper(integer'image(PEPos));

                -- Write to log line SIZE flit
                elsif flitCounter = 1 then

                    payloadSize := to_integer(unsigned(DataIn));

                    --write(inboundLogLine, integer'image(to_integer(unsigned(DataIn))) & " ");
                    lineHelper(integer'image(payloadSize));

                -- Write to log line ServiceID flit
                elsif flitCounter = 2 then

                    --write(inboundLogLine, CONV_STRING(DataIn) & " ");
                    lineHelper(CONV_STRING(DataIn));

                    service := DataIn;
                    serviceGo := True;

                end if;

                -- Decodes message payload flits according to ServiceID
                if serviceGo then

                    if service = DVFSServiceID then

                        if flitCounter = 3 then

                            -- Write DVFS config filt
                            --write(inboundLogLine, CONV_STRING(DataIn) & " ");
                            lineHelper(CONV_STRING(DataIn));

                        end if;

                    elsif service = SyntheticTrafficServiceID then

                        if flitCounter = 3 then

                            -- Write App ID
                            --write(inboundLogLine, integer'image(to_integer(unsigned(DataIn))) & " ");
                            lineHelper(integer'image(to_integer(unsigned(DataIn))));

                        elsif flitCounter = 4 then

                            -- Write Target Thread ID
                            --write(inboundLogLine, integer'image(to_integer(unsigned(DataIn))) & " ");
                            lineHelper(integer'image(to_integer(unsigned(DataIn))));

                        elsif flitCounter = 5 then

                            -- Write Source Thread ID
                            --write(inboundLogLine, integer'image(to_integer(unsigned(DataIn))) & " ");
                            lineHelper(integer'image(to_integer(unsigned(DataIn))));

                        end if;

                    -- OTHER SERVICE DECODING LOGIC GOES HERE -- 

                    else

                        report "Service ID <" & CONV_STRING(service) & "> unrecognized" severity error; 

                    end if;

                end if; 

                -- Update Checksum with new flit
                checksum := checksum + unsigned(DataIn);

                -- Increments counter if its less than current message size or SIZE flit has not yet been sent
                if (flitCounter < payloadSize + HeaderSize - 1) or (flitCounter < HeaderSize) then

                    flitCounter := flitCounter + 1;

                -- Whole message has been sent, increments message counter and reset flit counter
                else

                    -- Write to log file (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
                    inputTimestamp := NOW / 1 ns;
                    --write(inboundLogLine, integer'image(inputTimestamp) & " ");
                    --write(inboundLogLine, integer'image(to_integer(checksum)));
                    lineHelper(integer'image(inputTimestamp));
                    lineHelper(integer'image(to_integer(checksum)));
                    --writeline(inboundLog, inboundLogLine);

                    -- Reset interrupted values
                    if interrupted then

                        writeline(inboundLog, interruptedInboundLogLine);
                        interrupted := False;

                        -- Reset interrupted values
                        flitCounter := interruptedFlitCounter;
                        payloadSize := interruptedPayloadSize;
                        serviceGo := interruptedServiceGo;
                        checksum := interruptedChecksum;
                        --inputTimestamp := 0;

                    else

                        writeline(inboundLog, inboundLogLine);

                        -- Resets flags and counters
                        flitCounter := 0;
                        payloadSize := 0;
                        serviceGo := False;
                        checksum := (others =>'0');
                        --inputTimestamp := 0;

                    end if;

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
        variable checksum: unsigned(DataWidth - 1 downto 0)  := (others =>'0');

        variable outboundLogLine: line;
        
    begin

        if Reset = '1' then

            flitCounter := 0;
            payloadSize := 0;
            serviceGo := False;

            outputTimestamp := 0;
            checksum := (others =>'0');

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
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut))) & " ");

                        elsif flitCounter = 4 then

                            -- Write Target Thread ID
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut))) & " ");

                        elsif flitCounter = 5 then

                            -- Write Source Thread ID
                            write(outboundLogLine, integer'image(to_integer(unsigned(DataOut))) & " ");

                        end if;

                    -- OTHER SERVICE DECODING LOGIC GOES HERE -- 

                    else

                        report "Service ID <" & CONV_STRING(service) & "> unrecognized" severity warning; 

                    end if;

                end if; 

                -- Update Checksum with new flit
                checksum := checksum + unsigned(DataOut);

                -- Increments counter if its less than current message size or SIZE flit has not yet been sent
                if (flitCounter < payloadSize + HeaderSize - 1) or (flitCounter < HeaderSize) then

                    flitCounter := flitCounter + 1;

                -- Whole message has been sent, increments message counter and reset flit counter
                else

                    -- Write to log file (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
                    write(outboundLogLine, integer'image(outputTimestamp) & " ");
                    write(outboundLogLine, integer'image(to_integer(checksum)));
                    writeline(outboundLog, outboundLogLine);

                    -- Resets flags and counters
                    flitCounter := 0;
                    payloadSize := 0;
                    serviceGo := False;
                    checksum := (others =>'0');
                    outputTimestamp := 0;

                end if;

            end if;

        end if;

    end process;
	
end architecture RTL;
