--------------------------------------------------------------------------------
-- Title       : Trigger
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : Trigger.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Controls injector through Enable signal, which is determined based on Injector's FlowType value
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : 
--------------------------------------------------------------------------------

library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library JSON;
    use JSON.JSON.all;

library HyHeMPS;
    use HyHeMPS.HyHeMPS_PKG.all;
    use HyHeMPS.Injector_PKG.all;

--library work;
	--use work.HyHeMPS_PKG.all;
    --use work.JSON.all;


entity Trigger is
	
	generic(
        InjectorConfigFile   : string;
        PlatformConfigFile   : string
	);

	port(

		-- Basic
		--Clock : in std_logic;
		Reset : in std_logic;

		-- Input Interface (From Output Buffer)
		OutputBufferAvailableFlag : in std_logic;

		-- Input Interface (From Injector)
		LastFlitFlag: in std_logic; 

        -- Output Interface (To Injector)
        Enable : out std_logic;
        InjectorClock : out std_logic

	);
	
end entity Trigger;


architecture RTL of Trigger is

	-- JSON configuration files
    constant InjectorJSONConfig: T_JSON := jsonLoad(InjectorConfigFile);
    constant PlatformJSONConfig: T_JSON := jsonLoad(PlatformConfigFile);

    -- Message Flow type (Only "CBR" currently supported)
    constant FlowType: string(1 to 3) := jsonGetString(InjectorJSONConfig, "FlowType");
    constant SourceThreadName: string := jsonGetString(InjectorJSONConfig, "SourceThreadName");
    constant TargetThreadName: string := jsonGetString(InjectorJSONConfig, "TargetThreadName");
    constant Bandwidth: integer := jsonGetInteger(InjectorJSONConfig, "Bandwidth");  -- in MBps
    constant AppName: string := jsonGetString(InjectorJSONConfig, "AppName");
    constant AppID: integer := jsonGetInteger(InjectorJSONConfig, "AppID");
    constant InjectorClockPeriod: time := jsonGetReal(InjectorJSONConfig, "InjectorClockPeriod") * 1 ns;
    constant StartTime: time := jsonGetReal(InjectorJSONConfig, "StartTime") * 1 ns;
    constant StopTime: time := jsonGetReal(InjectorJSONConfig, "StopTime") * 1 ns;
    constant Periodic: boolean := jsonGetBoolean(InjectorJSONConfig, "Periodic");
    constant MaxAmountOfMessages: integer := jsonGetInteger(InjectorJSONConfig, "MSGAmount");

begin

	-- Certifies FlowType is "CBR" 
    --assert FlowType = "CBR" report "Error: FlowType <" & FlowType & "> is not recognized, only \"CBR\" FlowType is currently supported" severity <ERROR>;


    -- Defines Injector Clock
	InjectorClockGen: process begin

		if FlowType = "CBR" then

			InjectorClock <= '0';
	        wait for InjectorClockPeriod/2;
	        InjectorClock <= '1';
	        wait for InjectorClockPeriod/2;

	    end if;

	end process InjectorClockGen;


	-- Defines Injector enable based on FlowType
	CBRGen: if FlowType = "CBR" generate

		process
			variable ResetFallingEdgeTime: time := 0 ns;
			variable MessageCounter: integer := 0;
		begin

		  	while True loop

		  		if Reset = '1' then
		  			wait until Reset = '0';
		  			ResetFallingEdgeTime := now;
		  		end if;

		  		-- Enables associated injector
				wait for StartTime;
				report "Starting Flow <" & AppName & "." & SourceThreadName & " -- " & integer'image(Bandwidth) & " -> " & AppName & "." & TargetThreadName & ">" severity note;
				Enable <= '1';

				-- Flow doesnt have a StopTime, 0 and -1 are default values
				if StopTime /= -1 ns and StopTime /= 0 ns then
					wait for StopTime + ResetFallingEdgeTime;
					report "Stopping Flow <" & AppName & "." & SourceThreadName & " -- " & integer'image(Bandwidth) & " -> " & AppName & "." & TargetThreadName & ">" severity note;
					Enable <= '0';
				end if;

				-- Loops around if injector is periodic
				if not Periodic then
					exit;
				else
					ResetFallingEdgeTime := 0 ns;
				end if;

				-- Breaks loop if max amount of messages has been sent
				if LastFlitFlag = '1' then

					if MessageCounter = MaxAmountOfMessages - 1 then
						exit;
					else
						MessageCounter := MessageCounter + 1;
					end if;

				end if;
				
			end loop;

			-- Idles until simulation ends
			Enable <= '0';
            wait;

		end process;

	end generate CBRGen;

end architecture RTL;
