library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reg is
	port( clk, rst, en: in std_logic;
			input: in std_logic_vector( 7 downto 0 );
			output: out std_logic_vector( 7 downto 0 ) );
end reg;

architecture Behavioral of reg is
	component dff is
		port( clk, rst, en: in std_logic;
			input: in std_logic;
			output: out std_logic );
	end component;
begin

	reg_8: for n in 7 downto 0 generate
		reg: dff port map( clk => clk, rst => rst, en => en,
								 input => input(n), output => output(n) );
	end generate;

end Behavioral;

