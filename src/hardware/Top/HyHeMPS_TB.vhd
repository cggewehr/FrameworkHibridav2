--------------------------------------------------------------------------------
-- Title       : HyHeMPS test bench
-- Project     : HyHeMPS - Hybrid Hermes Multiprocessor System-on-Chip
--------------------------------------------------------------------------------
-- Authors     : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Instantiates HyHeMPS and configurable PEs
--------------------------------------------------------------------------------
-- Changelog   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : 
--------------------------------------------------------------------------------


library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

library work;
    use work.HyHeMPS_PKG.all;
    use work.JSON.all;


entity HyHeMPS_TB is

    generic(
        ProjectDir: string  -- Absolute path
    );
    
end entity HyHeMPS_TB;


architecture RTL of HyHeMPS_TB is

    constant PlatformConfigFile: string :=  ProjectDir & "/platform/PlatformConfig.json";
    constant PlatCFG: T_JSON := jsonLoad(PlatformConfigFile);

    constant ClusterClocksConfigFile: string := ProjectDir & "/platform/ClusterClocks.json";
    constant ClusterClocksCFG: T_JSON := jsonLoad(ClusterClocksConfigFile);

    constant AmountOfPEs: integer := jsonGetInteger(PlatCFG, "AmountOfPEs");
    constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
    constant NoCYSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/1");
    constant AmountOfNoCNodes: integer := NoCXSize * NoCYSize;

    --signal PEInterfaces: PEInterface_vector(0 to AmountOfPEs - 1);
    signal PEInputs: PEInputs_vector(0 to AmountOfPEs - 1);
    signal PEOutputs: PEOutputs_vector(0 to AmountOfPEs - 1);

    signal Reset: std_logic := '1';
    signal Clocks: std_logic_vector(0 to AmountOfNoCNodes - 1);
    constant ClockPeriods: real_vector(0 to AmountOfNoCNodes - 1) := jsonGetRealArray(ClusterClocksCFG, "ClusterClockPeriods");

    procedure GenerateClock(constant ClockPeriod: in time; signal Clock: out std_logic) is begin

        ClockLoop: loop

            Clock <= '0';
            wait for ClockPeriod/2;
            Clock <= '1';
            wait for ClockPeriod/2;
            
        end loop ClockLoop;
        
    end procedure GenerateClock;

begin

    -- Holds reset for 100 ns
    ResetProc: process begin

        Reset <= '1';
        wait for 100 ns;
        
        Reset <= '0';
        wait;

    end process ResetProc;


    -- Generates clocks for every router/wrapper
    ClockGen: for i in 0 to AmountOfNoCNodes - 1 generate

        GenerateClock(ClockPeriods(i) * 1 ns, Clocks(i));

    end generate ClockGen;


    -- Instantiates HyHeMPS
    HyHeMPSGen: entity work.HyHeMPS

        generic map(
            PlatformConfigFile => PlatformConfigFile,
            AmountOfPEs => AmountOfPEs,
            AmountOfNoCNodes => AmountOfNoCNodes
        )
        port map (
            Clocks => Clocks,
            Reset => Reset,
            --PEInterfaces => PEInterfaces
            PEInputs => PEInputs,
            PEOutputs => PEOutputs
        );


    -- Instantiates PEs (which then instantiate Injectors) to provide stimulus
    PEsGen: for i in 0 to AmountOfPEs - 1 generate

        PE: entity work.PE

            generic map(
                PlatformConfigFile  => PlatformConfigFile,
                PEConfigFile        => ProjectDir & "/flow/PE " & integer'image(i) & "/" & "PE " & integer'image(i) & ".json",
                --InjectorConfigFile  => "flow/INJ" & integer'image(i) & ".json",
                --InboundLogFilename  => "log/InLog" & integer'image(i) & ".txt",
                --OutboundLogFilename => "log/OutLog" & integer'image(i) & ".txt"
                ConfigPath => ProjectDir & "/flow/",
                LogPath => ProjectDir & "/log/"
            )
            port map(
                Reset   => Reset,
                ClockTx => PEOutputs(i).ClockTx,
                Tx      => PEOutputs(i).Tx,
                DataOut => PEOutputs(i).DataOut,
                CreditI => PEInputs(i).CreditI,
                ClockRx => PEInputs(i).ClockRx,
                Rx      => PEInputs(i).Rx,
                DataIn  => PEInputs(i).DataIn,
                CreditO => PEOutputs(i).CreditO
            );

            

    end generate PEsGEN;


end architecture RTL;
