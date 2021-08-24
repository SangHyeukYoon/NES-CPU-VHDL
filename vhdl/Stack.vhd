library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity Stack is
	port( clk, rst, en: in std_logic;
			push_pop: in std_logic;
			data_in: in std_logic_vector( 7 downto 0 );
			sp: out integer;
			data_out: out std_logic_vector( 7 downto 0 ));
end Stack;

architecture Behavioral of Stack is

	type mem is array( 0 to 31 ) of std_logic_vector( 7 downto 0 );
	signal stack_mem: mem := ( others => ( others => '0' ) );

begin

	process( clk, rst )
		variable stack_ptr: integer := 31;
	begin
		if rst = '1' then
			stack_ptr := 31;
			data_out <= ( others => '0' );
		elsif rising_edge(clk) then
			if en = '1' then
				if push_pop = '0' then -- push
					stack_mem(stack_ptr) <= data_in;
					
					if stack_ptr /= 0 then
						stack_ptr := stack_ptr - 1;
					end if;
				else -- pop
					data_out <= stack_mem(stack_ptr);
					
					if stack_ptr /= 31 then
						stack_ptr := stack_ptr + 1;
					end if;
				end if;
			end if;
		end if;
		
		sp <= stack_ptr;
	end process;

end Behavioral;

