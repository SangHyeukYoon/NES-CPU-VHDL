library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use WORK.STATE.ALL;

entity ALU is
	port( data_x, data_y: in std_logic_vector( 7 downto 0 );
			data_out: out std_logic_vector( 7 downto 0 );
			mode: in alu_op;
			carry_in: in std_logic;
			carry_out: out std_logic );
end ALU;

architecture Behavioral of ALU is

	component FullAdder is
		port( x, y, cin: in std_logic;
				s, c: out std_logic );
	end component;
	
	signal adc_sbc_carry: std_logic_vector( 7 downto 0 );
	signal adc_sbc_operand: std_logic_vector( 7 downto 0 );
	signal adc_sbc_result: std_logic_vector( 7 downto 0 );
	signal ora_result: std_logic_vector( 7 downto 0 );
	signal and_result: std_logic_vector( 7 downto 0 );
	signal eor_result: std_logic_vector( 7 downto 0 );
	signal cmp_result: std_logic_vector( 7 downto 0 );

begin

	process(data_y, mode)
	begin
		if mode = alu_adc then
			adc_sbc_operand <= data_y;
		elsif mode = alu_sbc then
			adc_sbc_operand <= not data_y;
		else
			adc_sbc_operand <= ( others => '0' );
		end if;
	end process;

	ALU0: FullAdder port map( x => data_x(0), y => adc_sbc_operand(0),
									  cin => carry_in,
									  s => adc_sbc_result(0),
									  c => adc_sbc_carry(0) );

	ALU_GEN:
	for I in 1 to 7 generate
		ALU: FullAdder port map( x => data_x(I), y => adc_sbc_operand(I),
										 cin => adc_sbc_carry( I - 1 ),
										 s => adc_sbc_result(I),
										 c => adc_sbc_carry(I) );
	end generate ALU_GEN;
	
	carry_out <= adc_sbc_carry(7);
	
	ora_result <= data_x or data_y;
	and_result <= data_x and data_y;
	eor_result <= data_x xor data_y;
	
	data_out <= adc_sbc_result when mode = alu_adc or mode = alu_sbc else
					ora_result when mode = alu_ora else
					and_result when mode = alu_and else
					eor_result when mode = alu_eor else
				   ( others => '0' );

end Behavioral;

