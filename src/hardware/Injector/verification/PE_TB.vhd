--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   16:49:48 06/05/2019
-- Design Name:   
-- Module Name:   /home/carlos/Desktop/GitKraken/DataManager/DataManagerTB.vhd
-- Project Name:  DataManager_MPEG
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: DataManager_NOC
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
-- Notes: 
-- This testbench has been automatically generated using types std_logic and
-- std_logic_vector for the ports of the unit under test.  Xilinx recommends
-- that these types always be used for the top-level I/O of a design in order
-- to guarantee that the testbench will bind correctly to the post-implementation 
-- simulation model.
--------------------------------------------------------------------------------
library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;
    
library work;
    use work.HyHeMPS_PKG.all;
    use work.Injector_PKG.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--USE ieee.numeric_std.ALL;
 
entity PE_TB is
end PE_TB;
 
architecture testbench OF PE_TB is 

    -- Basic
    signal Reset : std_logic := '0';
    
    -- Injector Interface
    signal CreditI : std_logic := '0';
    signal ClockRx : std_logic := '0';
    signal Rx : std_logic := '0';
    signal DataIn : std_logic_vector(31 downto 0) := (others => '0');
 
    -- Receiver Interface 
    signal ClockTx : std_logic;
    signal Tx : std_logic;
    signal DataOut : std_logic_vector(31 downto 0);
    signal CreditO : std_logic;

    -- Clock period definitions
    constant clock_period : time := 50 ns;
    
    constant ConfigPath: string := ".";
    constant LogPath: string := ".";
 
begin
 
    DUV: entity work.PE 
        generic map(
            PEConfigFile => "PESample.json",
            PlatformConfigFile => "InjectorSample.json",
            ConfigPath => ConfigPath,
            LogPath => LogPath
        )
        port map(

            -- Basic
            Reset => Reset,

            -- Receiver Interface    
            ClockTx => ClockTx,
            Tx => Tx,
            DataOut => DataOut,
            CreditI => CreditI,
            
            -- Injector Interface
            ClockRx => ClockRx,    
            Rx => Rx,
            DataIn => DataIn,
            CreditO => CreditO
        );

    -- Clock process definitions
    clockProcess: process
    begin

		    ClockRx <= '0';
		    wait for clock_period/2;
		    ClockRx <= '1';
		    wait for clock_period/2;
        
    end process;
 
    -- Stimulus process
    stimProcess: process begin		

    end process;

end architecture testbench;
