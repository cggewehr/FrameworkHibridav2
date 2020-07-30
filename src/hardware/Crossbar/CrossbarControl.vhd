--------------------------------------------------------------------------------
-- Title       : Crossbar interface module for HyHeMPS
-- Project     : HyHeMPS
--------------------------------------------------------------------------------
-- File        : CrossbarControl.vhd
-- Author      : Carlos Gewehr (carlos.gewehr@ecomp.ufsm.br)
-- Company     : UFSM, GMICRO (Grupo de Microeletronica)
-- Standard    : VHDL-1993
--------------------------------------------------------------------------------
-- Description : Handles messages from Crossbar to PE
--------------------------------------------------------------------------------
-- Revisions   : v0.01 - Initial implementation
--------------------------------------------------------------------------------
-- TODO        : Replace RX mux with OR gate, optimizing area 
--------------------------------------------------------------------------------


library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

library work;
	use work.HyHeMPS_PKG.all; 


entity CrossbarControl is

	generic (
		PEAddresses: HalfDataWidth_vector;
		SelfAddress: HalfDataWidth_t;
		IsStandalone: boolean
	);
	port (
		
		-- Basic
		Clock: in std_logic;
		Reset: in std_logic;

		-- Crossbar Interface
		DataInMux: in DataWidth_vector;
		RXMux: in std_logic_vector(PEAddresses'range);
		CreditO: out std_logic_vector(PEAddresses'range);
		NewGrant: in std_logic;

		-- PE Interface
		PEDataIn: out DataWidth_t;
		PERx: out std_logic;
		PECreditO: in std_logic 

	);
	
end entity CrossbarControl;


architecture RTL of CrossbarControl is

	-- Returns index of active tx (by extension, ID of source PE)
	function GetIndexOfActiveTx(txArray: std_logic_vector) return integer is begin

		for i in txArray'range loop 

			if txArray(i) = '1' then
				return i;

			end if;

		end loop;

		return 0;  -- Defaults to 0 so no latch is synthesized 
		
	end function GetIndexOfActiveTx;


	-- Performs "or" operation between all elements of a given std_logic_vector
	function OrReduce(inputArray: std_logic_vector) return std_logic is
		variable orReduced: std_logic := '0';
	begin

		for i in inputArray'range loop 

			orReduced := orReduced or inputArray(i);

		end loop;

		return orReduced;
		
	end function OrReduce;


    -- Searches through a given list of addresses of PEs contained in this crossbar, and returns index of a given address in given list of addresses,
    -- which matches the MUX selector value which produces the data value associated with the given address
	function GetIndexOfAddr(Addresses: HalfDataWidth_vector; AddressOfInterest: HalfDataWidth_t; IndexToSkip: integer) return integer is begin

		for i in 0 to Addresses'high - 1 loop  -- Ignores wrapper (Last element of Addresses[])

			if i = IndexToSkip then
				next;

			elsif Addresses(i) = AddressOfInterest then
				return i;

			end if;

		end loop;

		return 0;  -- Return index of wrapper if given ADDR was not found in crossbar
		
	end function GetIndexOfAddr;

	constant selfIndex: integer := GetIndexOfAddr(PEAddresses, SelfAddress, 0);
	signal sourceIndex: integer;
	
	-- Inverts ADDR flit of every new message going through the wrapper if crossbar is integrated in HyHeMPS
	signal crossbarDataInv: DataWidth_t;

begin

	process(Clock) begin

		if rising_edge(Clock) then

			if Reset = '1' then
				sourceIndex <= 0;

			else
				sourceIndex <= GetIndexOfActiveTx(RXMux);

			end if;

		end if;

	end process;

    -- Mutiplexes DataIn based on "sourceIndex"
	PEDataIn <= DataInMux(sourceIndex);

    -- Mutiplexes Rx based on "sourceIndex"
	PERx <= OrReduce(RXMux);
	
	-- Mutiplexes CreditI based on "sourceIndex"
	CreditO <= (selfIndex => PECreditO, others => '0');
	
end architecture RTL;
