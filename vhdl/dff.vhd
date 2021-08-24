library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity dff is
	port( clk, rst, en: in std_logic;
			input: in std_logic;
			output: out std_logic );
end dff;

architecture Behavioral of dff is
	signal data: std_logic;
begin

	process( clk, rst, en )
	begin
		if rst = '1' then
			data <= '0';
		elsif rising_edge(clk) then
			if en = '1' then
				data <= input;
			else
				data <= data;
			end if;
		end if;
	end process;
	
	output <= data;
	
end Behavioral;

