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
    
end entity HyHeMPS_TB;


architecture RTL of HyHeMPS_TB is
    constant PlatformConfigFile: string :=  "platform/PlatformConfig.json";
    constant PlatCFG: T_JSON := jsonLoad(PlatformConfigFile);

    constant ClusterClocksConfigFile: string := "platform/ClusterClocks.json";
    constant ClusterClocksCFG: T_JSON := jsonLoad(ClusterClocksConfigFile);

    constant AmountOfPEs: integer := jsonGetInteger(PlatCFG, "AmountOfPEs");
    constant NoCXSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/0");
    constant NoCYSize: integer := jsonGetInteger(PlatCFG, "BaseNoCDimensions/1");
    constant AmountOfNoCNodes: integer := NoCXSize * NoCYSize;

    signal PEInterfaces: PEInterface_vector(0 to AmountOfPEs - 1);

    signal Reset: std_logic := '1';
    signal Clocks: std_logic_vector(0 to AmountOfNoCNodes - 1);

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
    Reset <= '1', '0' after 100 ns;

    -- Generates clocks for every router/wrapper
    ClockGen: for i in 0 to AmountOfNoCNodes - 1 generate
        signal ClockPeriods: real_vector(0 to AmountOfNoCNodes - 1);
    begin
        ClockPeriods(i) <= jsonGetReal(ClusterClocksCFG, "ClusterClockPeriods/" & integer'image(i));
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
            PEInterfaces => PEInterfaces
        );


    -- Instantiates PEs (which then instantiate Injectors) to provide stimulus
    PEsGen: for i in 0 to AmountOfPEs - 1 generate

        PE: entity work.PE

            generic map(
                PlatformConfigFile  => PlatformConfigFile,
                PEConfigFile        => "flow/PE" & integer'image(i) & ".json",
                InjectorConfigFile  => "flow/INJ" & integer'image(i) & ".json",
                InboundLogFilename  => "log/InLog" & integer'image(i) & ".txt",
                OutboundLogFilename => "log/OutLog" & integer'image(i) & ".txt"
            )
            port map (
                Reset   => Reset,
                ClockTx => PEInterfaces(i).ClockTx,
                Tx      => PEInterfaces(i).Tx,
                DataOut => PEInterfaces(i).DataOut,
                CreditI => PEInterfaces(i).CreditI,
                ClockRx => PEInterfaces(i).ClockRx,
                Rx      => PEInterfaces(i).Rx,
                DataIn  => PEInterfaces(i).DataIn,
                CreditO => PEInterfaces(i).CreditO
            );

    end generate PEsGEN;


end architecture RTL;
