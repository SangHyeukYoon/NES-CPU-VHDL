library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity cont is
	port( instruction: in std_logic_vector( 7 downto 0 );
			bjrr, bi, jmp, bran, pppp, cs, inxy, sly, cc, oaea, slcs, arlr, slx, di: out std_logic);
end cont;

architecture Behavioral of cont is

	signal bjrr_sig: std_logic;
	signal bi_sig: std_logic;
	signal jmp_sig: std_logic;
	signal bran_sig: std_logic;
	signal pppp_sig: std_logic;
	signal cs_sig: std_logic;
	signal inxy_sig: std_logic;
	signal sly_sig: std_logic;
	signal cc_sig: std_logic;
	signal oaea_sig: std_logic;
	signal slcs_sig: std_logic;
	signal arlr_sig: std_logic;
	signal slx_sig: std_logic;
	signal di_sig: std_logic;

begin

	bjrr_sig <= '0';
	bi_sig <= '0';
	jmp_sig <= '0';
	bran_sig <= '0';
	pppp_sig <= '0';
	cs_sig <= '0';
	inxy_sig <= '0';
	sly_sig <= '0';
	cc_sig <= '0';
	oaea_sig <= '0';
	slcs_sig <= '0';
	arlr_sig <= '0';
	slx_sig <= '0';
	di_sig <= '0';

	process(instruction)
	begin
		if instruction(7) = '0' and instruction( 4 downto 0 ) = "00000" then
			bjrr_sig <= '1';
		elsif instruction( 7 downto 4 ) = "0010" and instruction( 2 downto 0 ) = "100" then
			bi_sig <= '1';
		end if;
	end process;
	
	bjrr <= bjrr_sig;
	bi <= bi_sig;
	jmp <= jmp_sig;
	bran <= bran_sig;
	pppp <= pppp_sig;
	cs <= cs_sig;
	inxy <= inxy_sig;
	sly <= sly_sig;
	cc <= cc_sig;
	oaea <= oaea_sig;
	slcs <= slcs_sig;
	arlr <= arlr_sig;
	slx <= slx_sig;
	di <= di_sig;

end Behavioral;

