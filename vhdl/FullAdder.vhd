library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity FullAdder is
	port( x, y, cin: in std_logic;
			s, c: out std_logic);
end FullAdder;

architecture Behavioral of FullAdder is

	signal xor1: std_logic;
	signal and1: std_logic;
	signal and2: std_logic;

begin	
	xor1 <= x xor y;
	and1 <= x and y;
			
	s <= xor1 xor cin;
	and2 <= xor1 and cin;
			
	c <= and2 or and1;
end Behavioral;

