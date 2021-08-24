library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
--use IEEE.STD_LOGIC_ARITH.ALL; 
use IEEE.NUMERIC_STD.ALL;

use WORK.STATE.ALL;

entity ram is
	port( clk, rst: in std_logic;
			mode: in ram_mode;
			adr: in std_logic_vector( 7 downto 0 );
			adr_16: in std_logic_vector( 15 downto 0 );
			input: in std_logic_vector( 7 downto 0 );
			output:out std_logic_vector( 7 downto 0 );
			output_16:out std_logic_vector( 15 downto 0 ) );
end ram;

architecture Behavioral of ram is
	component reg is
		port( clk, rst, en: in std_logic;
				input: in std_logic_vector( 7 downto 0 );
				output: out std_logic_vector( 7 downto 0 ) );
	end component;

	type data_out_t is array ( 7 downto 0 ) of std_logic_vector( 7 downto 0 );
	signal data_out: data_out_t;
	
	signal en: std_logic_vector( 7 downto 0 );
	--signal address: integer range 0 to 2048 := 0;
begin

	input_mode: process( adr, mode )
	begin
		en <= ( others => '0' );
		
		if mode = adr_in then
			en(to_integer(unsigned(adr))) <= '1';
		end if;
	end process;
	
	gen_ram:
	for I in 7 downto 0 generate
		reg_ram: reg port map( clk => clk, rst => rst,
									  en => en(I),
									  input => input,
									  output => data_out(I) );
	end generate;

	output <= data_out(to_integer(unsigned(adr)));

end Behavioral;

