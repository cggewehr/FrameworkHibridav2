--------------------------------------------------------------------------------
-- Title       : Hermes top level block
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- Authors     : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Instantiates a Hermes NoC with mesh topology, replacing Routers
--		         with Wrappers as necessary
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


entity Hermes is

	generic(
		NoCXSize: integer;
		NoCYSize: integer
	);
	port(
		Clocks: std_logic_vector;
		Reset: std_logic;
		--LocalPortInterfaces: inout RouterPort_vector
		LocalPortInterfaces: inout PEInterface_vector
	);
	
end entity Hermes;


architecture Mesh of Hermes is

    constant AmountOfNoCNodes: integer := NoCXSize * NoCYSize;

    signal RouterInterfaces: RouterInterface_vector(0 to AmountOfNoCNodes - 1);

begin
	
    -- Instantiates and connects NoC routers and wrappers, if any
    NoCGen: for i in 0 to AmountOfNoCNodes - 1 generate

        Router: entity work.RouterCC

            generic map(
                Address => RouterAddress(i, NoCXSize)  -- From HyHeMPS_PKG
            )
            port map(

                -- Basic
                Clock    => Clocks(i),
                Reset    => Reset,

                -- Input interface
                Clock_Rx => RouterInterfaces(i).ClockRx,
                Rx       => RouterInterfaces(i).Rx,
                Data_in  => RouterInterfaces(i).DataIn,
                Credit_o => RouterInterfaces(i).CreditO,

                -- Output interface
                Clock_Tx => RouterInterfaces(i).ClockTx,
                Tx       => RouterInterfaces(i).Tx,
                Data_out => RouterInterfaces(i).DataOut,
                Credit_i => RouterInterfaces(i).CreditI

            );

        assert false report "Instantiated a router/wrapper at base NoC position " & integer'image(i) &
        " = (" & integer'image(i / NoCXSize) & "," & integer'image(i mod NoCXSize) & ")" severity note;

        -- Maps this router's south port to the north port of the router below it 
        SouthMap: if i >= NoCXSize generate

            RouterInterfaces(i).ClockRx(South) <= RouterInterfaces(i - NoCXSize).ClockTx(North);
            RouterInterfaces(i).Rx(South) <= RouterInterfaces(i - NoCXSize).Tx(North);
            RouterInterfaces(i).DataIn(South) <= RouterInterfaces(i - NoCXSize).DataOut(North);
            RouterInterfaces(i).CreditI(South) <= RouterInterfaces(i - NoCXSize).CreditO(North);

            assert false report "Mapped south port of router/wrapper " & integer'image(i) & " to north port of router/wrapper " & integer'image(i - NoCXSize) severity note;

        end generate SouthMap;


        -- Grounds this router's south port, since this router has no router below it
        SouthGround: if i < NoCXSize generate

            RouterInterfaces(i).ClockRx(South) <= '0';
            RouterInterfaces(i).Rx(South) <= '0';
            RouterInterfaces(i).DataIn(South) <= (others=>'0');
            RouterInterfaces(i).CreditI(South) <= '0';

            assert false report "Grounded south port of router/wrapper " & integer'image(i) severity note;

        end generate SouthGround;


        -- Maps this router's north port to the south port of the router above it
        NorthMap: if i < NoCXSize * (NoCYSize - 1) generate

            RouterInterfaces(i).ClockRx(North) <= RouterInterfaces(i + NoCXSize).ClockTx(North);
            RouterInterfaces(i).Rx(North) <= RouterInterfaces(i + NoCXSize).Tx(South);
            RouterInterfaces(i).DataIn(North) <= RouterInterfaces(i + NoCXSize).DataOut(South);
            RouterInterfaces(i).CreditI(North) <= RouterInterfaces(i + NoCXSize).CreditO(South);

            assert false report "Mapped north port of router/wrapper " & integer'image(i) & " to south port of router/wrapper " & integer'image(i + NoCXSize) severity note;

        end generate NorthMap;


        -- Grounds this router's north port, since this router has no router above it 
        NorthGround: if i >= NoCXSize * (NoCYSize - 1) generate

            RouterInterfaces(i).ClockRx(North) <= '0';
            RouterInterfaces(i).Rx(North) <= '0';
            RouterInterfaces(i).DataIn(North) <= (others=>'0');
            RouterInterfaces(i).CreditI(North) <= '0';

            assert false report "Grounded north port of router/wrapper " & integer'image(i) severity note;

        end generate NorthGround;


        -- Maps this router's west port to the east port of the router to its right
        WestMap: if i mod NoCXSize /= 0 generate

            RouterInterfaces(i).ClockRx(West) <= RouterInterfaces(i + 1).ClockTx(East);
            RouterInterfaces(i).Rx(West) <= RouterInterfaces(i + 1).Tx(East);
            RouterInterfaces(i).DataIn(West) <= RouterInterfaces(i + 1).DataOut(East);
            RouterInterfaces(i).CreditI(West) <= RouterInterfaces(i + 1).CreditO(East);

            assert false report "Mapped west port of router/wrapper " & integer'image(i) & " to east port of router/wrapper " & integer'image(i + 1) severity note;

        end generate WestMap;


        -- Grounds this router's west port, since this router has no router to its right
        WestGround: if i mod NoCXSize = 0 generate

            RouterInterfaces(i).ClockRx(West) <= '0';
            RouterInterfaces(i).Rx(West) <= '0';
            RouterInterfaces(i).DataIn(West) <= (others=>'0');
            RouterInterfaces(i).CreditI(West) <= '0';

            assert false report "Grounded west port of router/wrapper " & integer'image(i) severity note;

        end generate WestGround;


        -- Maps this router's east port to the east port of the router to its left
        EastMap: if i mod NoCXSize /= NoCXSize - 1 generate

            RouterInterfaces(i).ClockRx(East) <= RouterInterfaces(i - 1).ClockTx(West);
            RouterInterfaces(i).Rx(East) <= RouterInterfaces(i - 1).Tx(West);
            RouterInterfaces(i).DataIn(East) <= RouterInterfaces(i - 1).DataOut(West);
            RouterInterfaces(i).CreditI(East) <= RouterInterfaces(i - 1).CreditO(West);

            assert false report "Mapped east port of router/wrapper " & integer'image(i) & " to west port of router/wrapper " & integer'image(i - 1) severity note;

        end generate EastMap;


        -- Grounds this router's east port, since this router has no router to its left
        EastGround: if i mod NoCXSize = NoCXSize - 1 generate

            RouterInterfaces(i).ClockRx(East) <= '0';
            RouterInterfaces(i).Rx(East) <= '0';
            RouterInterfaces(i).DataIn(East) <= (others=>'0');
            RouterInterfaces(i).CreditI(East) <= '0';

            assert false report "Grounded east port of router/wrapper " & integer'image(i) severity note;

        end generate EastGround;

    end generate NoCGen;


    -- Generates entity interface (Local port of every router
    InterfaceGen: for i in 0 to AmountOfNoCNodes - 1 generate

        -- Input interface
        RouterInterfaces(i).ClockRx(Local) <= LocalPortInterfaces(i).ClockRx;
        RouterInterfaces(i).Rx(Local) <= LocalPortInterfaces(i).Rx;
        RouterInterfaces(i).DataIn(Local) <= LocalPortInterfaces(i).DataIn;
        LocalPortInterfaces(i).CreditO <= RouterInterfaces(i).CreditO(Local);

        -- Output interface
        LocalPortInterfaces(i).ClockTx <= RouterInterfaces(i).ClockTx(Local);
        LocalPortInterfaces(i).Tx <= RouterInterfaces(i).Tx(Local);
        LocalPortInterfaces(i).DataOut <= RouterInterfaces(i).DataOut(Local);
        RouterInterfaces(i).CreditI(Local) <= LocalPortInterfaces(i).CreditI;

    end generate InterfaceGen;
	
end architecture Mesh;
