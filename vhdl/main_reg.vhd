library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use WORK.STATE.ALL;

entity main_reg is
	port( clk, rst: in std_logic;
			mode: in reg_mode;
			status_mode: in reg_status;
			input: in std_logic_vector( 7 downto 0 );
			output: out std_logic_vector( 7 downto 0 );
			status: out std_logic_vector( 7 downto 0 ) );
end main_reg;

architecture Behavioral of main_reg is
	component dff is
		port( clk, rst, en: in std_logic;
				input: in std_logic;
				output: out std_logic );
	end component;
	
	component reg is
		port( clk, rst, en: in std_logic;
				input: in std_logic_vector( 7 downto 0 );
				output: out std_logic_vector( 7 downto 0 ) );
	end component;

	signal output_A: std_logic_vector( 7 downto 0 );
	signal en_A: std_logic;

	signal output_X: std_logic_vector( 7 downto 0 );
	signal en_X: std_logic;

	signal output_Y: std_logic_vector( 7 downto 0 );
	signal en_Y: std_logic;
	
	signal input_negative: std_logic;
	signal en_negative: std_logic;
	
	signal input_overflow: std_logic;
	signal en_overflow: std_logic;
	
	signal input_decimal: std_logic;
	signal en_decimal: std_logic;
	
	signal input_interrupt: std_logic;
	signal en_interrupt: std_logic;
	
	signal input_zero: std_logic;
	signal en_zero: std_logic;
	
	signal input_carry: std_logic;
	signal en_carry: std_logic;
	
	signal output_status: std_logic_vector( 7 downto 0 );
begin

	input_mode: process( mode )
	begin
		if mode = A_in then
			en_A <= '1';
			
			en_X <= '0';
			en_Y <= '0';
		elsif mode = X_in then
			en_X <= '1';
			
			en_A <= '0';
			en_Y <= '0';
		elsif mode = Y_in then
			en_Y <= '1';
			
			en_A <= '0';
			en_X <= '0';
		else
			en_A <= '0';
			en_X <= '0';
			en_Y <= '0';
		end if;
	end process;
	
	status_modes: process(status_mode)
	begin
		en_negative <= '0';
		en_overflow <= '0';
		en_decimal <= '0';
		en_interrupt <= '0';
		en_zero <= '0';
		en_carry <= '0';
		
		input_negative <= '0';
		input_overflow <= '0';
		input_decimal <= '0';
		input_interrupt <= '0';
		input_zero <= '0';
		input_carry <= '0';
		
		if status_mode(5) = set then
			en_negative <= '1';
			input_negative <= '1';
		elsif status_mode(5) = clear then
			en_negative <= '1';
		end if;
		
		if status_mode(4) = set then
			en_overflow <= '1';
			input_overflow <= '1';
		elsif status_mode(4) = clear then
			en_overflow <= '1';
		end if;
		
		if status_mode(3) = set then
			en_decimal <= '1';
			input_decimal <= '1';
		elsif status_mode(3) = clear then
			en_decimal <= '1';
		end if;
		
		if status_mode(2) = set then
			en_interrupt <= '1';
			input_interrupt <= '1';
		elsif status_mode(2) = clear then
			en_interrupt <= '1';
		end if;
		
		if status_mode(1) = set then
			en_zero <= '1';
			input_zero <= '1';
		elsif status_mode(1) = clear then
			en_zero <= '1';
		end if;
		
		if status_mode(0) = set then
			en_carry <= '1';
			input_carry <= '1';
		elsif status_mode(0) = clear then
			en_carry <= '1';
		end if;
	end process;
	
	reg_A: reg port map( clk => clk, rst => rst, en => en_A,
								input => input, output => output_A );

	reg_X: reg port map( clk => clk, rst => rst, en => en_X,
								input => input, output => output_X );

	reg_Y: reg port map( clk => clk, rst => rst, en => en_Y,
								input => input, output => output_Y );

	negative: dff port map( clk => clk, rst => rst, en => en_negative,
									input => input_negative, output => output_status(7) );

	overflow: dff port map( clk => clk, rst => rst, en => en_overflow,
									input => input_overflow, output => output_status(6) );

	decimal: dff port map( clk => clk, rst => rst, en => en_decimal,
									input => input_decimal, output => output_status(3) );

	interrupt: dff port map( clk => clk, rst => rst, en => en_interrupt,
									input => input_interrupt, output => output_status(2) );

	zero: dff port map( clk => clk, rst => rst, en => en_zero,
									input => input_zero, output => output_status(1) );

	carry: dff port map( clk => clk, rst => rst, en => en_carry,
									input => input_carry, output => output_status(0) );

	output_mode: process( mode, output_A, output_X, output_Y )
	begin
		if mode = A_out then
			output <= output_A;
		elsif mode = X_out then
			output <= output_X;
		elsif mode = Y_out then
			output <= output_Y;
		else
			output <= ( others => '0' );
		end if;
	end process;

	output_status(5) <= '1';
	output_status(4) <= '1';
	
	status <= output_status;

end Behavioral;

