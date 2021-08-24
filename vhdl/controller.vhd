library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use WORK.STATE.ALL;

entity controller is
	port( clk, rst: in std_logic;
			instruction: in std_logic_vector( 7 downto 0 );
			current_state: out state ); -- debugging
end controller;

architecture Behavioral of controller is
	signal cs, nxs: state;
begin

	state_reg: process(clk, rst)
	begin
		if rst = '1' then
			cs <= zero_state;
		elsif rising_edge(clk) then
			cs <= nxs;
		end if;
	end process;
	
	next_state: process(cs)
	begin
		case cs is
			-- The state of zero. Set PC as 0.
			when zero_state => nxs <= ins_fetch;
			-- Wait for fetching instruction.
			when ins_fetch => nxs <= ins_decode;
			
			when ins_decode =>
				if instruction( 1 downto 0 ) = "01" then
					case instruction( 4 downto 2 ) is
						-- absolute
						when "011" =>
							-- sta: reg_out => A, ins_fetch => 2
							if instruction( 7 downto 5 ) = "100" then
								nxs <= abs_sta_ready;
							else
								nxs <= abs_ins_fetch_2;
							end if;
						-- absolute, x
						when "111" => nxs <= abs_x_add_adr;
						-- absolute, y
						when "110" => nxs <= abs_y_add_adr;
						-- zeropage
						when "001" =>
							-- sta: reg_out => A, ins_fetch => 2
							if instruction( 7 downto 5 ) = "100" then
								nxs <= zeropage_sta_ready;
							else
								nxs <= zeropage_ins_fetch_1;
							end if;
						-- zeropage, x
						when "101" => nxs <= zero_x_ins_fetch_1;
						-- indirect, x
						when "000" => nxs <= indirect_x_adr_ready;
						-- indirect, y
						when "100" => nxs <= indirect_y_read_mem;
						-- immediate
						when "010" =>
							case instruction( 7 downto 5 ) is
								when "101" => nxs <= imm_lda_ready;
								when "000" => nxs <= imm_ora_ready;
								when "001" => nxs <= imm_and_ready;
								when "010" => nxs <= imm_eor_ready;
								when "011" => nxs <= imm_adc_ready;
								when "110" => nxs <= imm_cmp_ready;
								when "111" => nxs <= imm_sbc_ready;
								
								when others => nxs <= error;
							end case;
						when others => nxs <= error;
					end case;
				else
					nxs <= error;
				end if;
			
			-- abs_sta
			when abs_sta_ready => nxs <= abs_sta;
			when abs_ins_fetch_2 =>
				case instruction( 7 downto 5 ) is
					-- abs_lda
					when "101" => nxs <= abs_lda_ready;
					-- abs alu operations: reg_out => A, data_out, alu_op
					when "000" => nxs <= abs_ora_ready;
					when "001" => nxs <= abs_and_ready;
					when "010" => nxs <= abs_eor_ready;
					when "011" => nxs <= abs_adc_ready;
					when "110" => nxs <= abs_cmp_ready;
					when "111" => nxs <= abs_sbc_ready;
					
					when others => nxs <= error;
				end case;
			
			-- abs_lda
			when abs_lda_ready => nxs <= alu_lda;
			-- abs alu operation results: write to register
			when abs_ora_ready => nxs <= alu_ora;
			when abs_and_ready => nxs <= alu_and;
			when abs_eor_ready => nxs <= alu_eor;
			when abs_adc_ready => nxs <= alu_adc;
			when abs_cmp_ready => nxs <= alu_cmp;
			when abs_sbc_ready => nxs <= alu_sbc;
			
			-- abs, x operations
			when abs_x_add_adr | abs_y_add_adr =>
				case instruction( 7 downto 5 ) is
					-- abs_xy_sta
					when "100" => nxs <= abs_xy_sta_ready;
					-- abs_xy_lda
					when "101" => nxs <= abs_xy_lda_ready;
					-- abs_xy alu operations: reg_out => A, data_out, alu_op
					when "000" => nxs <= abs_xy_ora_ready;
					when "001" => nxs <= abs_xy_and_ready;
					when "010" => nxs <= abs_xy_eor_ready;
					when "011" => nxs <= abs_xy_adc_ready;
					when "110" => nxs <= abs_xy_cmp_ready;
					when "111" => nxs <= abs_xy_sbc_ready;
					
					when others => nxs <= error;
				end case;
			
			-- abs_xy_sta
			when abs_xy_sta_ready => nxs <= abs_xy_sta;
			-- abs_xy_lda
			when abs_xy_lda_ready => nxs <= alu_lda;
			-- abs_xy alu operations results: write to register
			when abs_xy_ora_ready => nxs <= alu_ora;
			when abs_xy_and_ready => nxs <= alu_and;
			when abs_xy_eor_ready => nxs <= alu_eor;
			when abs_xy_adc_ready => nxs <= alu_adc;
			when abs_xy_cmp_ready => nxs <= alu_cmp;
			when abs_xy_sbc_ready => nxs <= alu_sbc;
			
			-- zeropage operations
			when zeropage_ins_fetch_1 =>
				case instruction( 7 downto 5 ) is
					when "101" => nxs <= zeropage_lda_ready;
					when "000" => nxs <= zeropage_ora_ready;
					when "001" => nxs <= zeropage_and_ready;
					when "010" => nxs <= zeropage_eor_ready;
					when "011" => nxs <= zeropage_adc_ready;
					when "110" => nxs <= zeropage_cmp_ready;
					when "111" => nxs <= zeropage_sbc_ready;
					
					when others => nxs <= error;
				end case;
			
			-- zeropage sta
			when zeropage_sta_ready => nxs <= zeropage_sta;
			-- zeropage lda
			when zeropage_lda_ready => nxs <= alu_lda;
			-- zeropage operation results: write to register
			when zeropage_ora_ready => nxs <= alu_ora;
			when zeropage_and_ready => nxs <= alu_and;
			when zeropage_eor_ready => nxs <= alu_eor;
			when zeropage_adc_ready => nxs <= alu_adc;
			when zeropage_cmp_ready => nxs <= alu_cmp;
			when zeropage_sbc_ready => nxs <= alu_sbc;
			
			-- zeropage, x operations
			when zero_x_ins_fetch_1 =>
				case instruction( 7 downto 5 ) is
					--zeropage, x sta: reg_out => A
					when "100" => nxs <= zero_x_sta_ready;
					when "101" => nxs <= zero_x_lda_ready;
					when "000" => nxs <= zero_x_ora_ready;
					when "001" => nxs <= zero_x_and_ready;
					when "010" => nxs <= zero_x_eor_ready;
					when "011" => nxs <= zero_x_adc_ready;
					when "110" => nxs <= zero_x_cmp_ready;
					when "111" => nxs <= zero_x_sbc_ready;
					
					when others => nxs <= error;
				end case;
			
			-- zeropage, x sta
			when zero_x_sta_ready => nxs <= zero_x_sta;
			-- zeropage, x lda
			when zero_x_lda_ready => nxs <= alu_lda;
			--zeropage, x operation results: write to register
			when zero_x_ora_ready => nxs <= alu_ora;
			when zero_x_and_ready => nxs <= alu_and;
			when zero_x_eor_ready => nxs <= alu_eor;
			when zero_x_adc_ready => nxs <= alu_adc;
			when zero_x_cmp_ready => nxs <= alu_cmp;
			when zero_x_sbc_ready => nxs <= alu_sbc;
			
			-- indirect, y address ready
			when indirect_y_read_mem => nxs <= indirect_y_adr_ready;
			
			--indirect, xy address
			when indirect_x_adr_ready | indirect_y_adr_ready =>
				if instruction( 7 downto 5 ) = "100" then
					nxs <= indirect_xy_sta_ready;
				else
					nxs <= indirect_xy_adr;
				end if;
			
			--indirect, xy common operations
			when indirect_xy_adr =>
				case instruction( 7 downto 5 ) is
					when "101" => nxs <= indirect_xy_lda_ready;
					when "000" => nxs <= indirect_xy_ora_ready;
					when "001" => nxs <= indirect_xy_and_ready;
					when "010" => nxs <= indirect_xy_eor_ready;
					when "011" => nxs <= indirect_xy_adc_ready;
					when "110" => nxs <= indirect_xy_cmp_ready;
					when "111" => nxs <= indirect_xy_sbc_ready;
					
					when others => nxs <= error;
				end case;
			
			-- indirect, xy common sta
			when indirect_xy_sta_ready => nxs <= indirect_xy_sta;
			-- indirect, xy common lda
			when indirect_xy_lda_ready => nxs <= alu_lda;
			-- indirect, xy common operation results: write to register;
			when indirect_xy_ora_ready => nxs <= alu_ora;
			when indirect_xy_and_ready => nxs <= alu_and;
			when indirect_xy_eor_ready => nxs <= alu_eor;
			when indirect_xy_adc_ready => nxs <= alu_adc;
			when indirect_xy_cmp_ready => nxs <= alu_cmp;
			when indirect_xy_sbc_ready => nxs <= alu_sbc;
			
			-- immediate lda
			when imm_lda_ready => nxs <= imm_lda;
			-- immediate operation results
			when imm_ora_ready => nxs <= alu_ora;
			when imm_and_ready => nxs <= alu_and;
			when imm_eor_ready => nxs <= alu_eor;
			when imm_adc_ready => nxs <= alu_adc;
			when imm_cmp_ready => nxs <= alu_cmp;
			when imm_sbc_ready => nxs <= alu_sbc;
			
			-- final states
			when alu_ora | alu_and | alu_eor| alu_adc | 
				  alu_cmp | alu_sbc | alu_lda =>
					nxs <= ins_fetch;
			
			when abs_sta | abs_xy_sta | zeropage_sta | zero_x_sta | 
				  indirect_xy_sta | imm_lda =>
					nxs <= ins_fetch;
			
			when error => 
				report "error";
				nxs <= error;
			
			when others => nxs <= error;
		end case;
	end process;
	
	current_state <= cs;

end Behavioral;

