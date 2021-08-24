library IEEE;
use IEEE.STD_LOGIC_1164.all;

package state is
	type state is ( -- basic state
						 zero_state, ins_fetch, ins_decode, error,
						 -- abs state
						 abs_ins_fetch_2,
						 abs_sta_ready, abs_lda_ready, abs_ora_ready, abs_and_ready,
						 abs_eor_ready, abs_adc_ready, abs_cmp_ready, abs_sbc_ready,
						 abs_sta,
						 -- abs, x state
						 abs_x_add_adr,
						 -- abs, y state
						 abs_y_add_adr,
						 -- abs, xy common state
						 abs_xy_sta_ready, abs_xy_lda_ready, abs_xy_ora_ready, abs_xy_and_ready,
						 abs_xy_eor_ready, abs_xy_adc_ready, abs_xy_cmp_ready, abs_xy_sbc_ready,
						 abs_xy_sta,
						 -- zeropage state
						 zeropage_ins_fetch_1,
						 zeropage_sta_ready, zeropage_lda_ready, zeropage_ora_ready,
						 zeropage_and_ready, zeropage_eor_ready, zeropage_adc_ready,
						 zeropage_cmp_ready, zeropage_sbc_ready,
						 zeropage_sta,
						 -- zeropage, x state
						 zero_x_ins_fetch_1, -- fetch 1bytes and register x.
						 zero_x_sta_ready, zero_x_lda_ready, zero_x_ora_ready, zero_x_and_ready,
						 zero_x_eor_ready, zero_x_adc_ready, zero_x_cmp_ready, zero_x_sbc_ready,
						 zero_x_sta,
						 -- indirect, x state
						 indirect_x_adr_ready,
						 -- indirect, y state
						 indirect_y_read_mem, indirect_y_adr_ready,
						 -- indirect, xy common state
						 indirect_xy_adr,
						 indirect_xy_sta_ready, indirect_xy_lda_ready, indirect_xy_ora_ready,
						 indirect_xy_and_ready, indirect_xy_eor_ready, indirect_xy_adc_ready,
						 indirect_xy_cmp_ready, indirect_xy_sbc_ready,
						 indirect_xy_sta,
						 -- immediate
						 imm_lda_ready, imm_lda,
						 imm_ora_ready, imm_and_ready, imm_eor_ready,
						 imm_adc_ready, imm_cmp_ready, imm_sbc_ready,
						 -- common
						 alu_lda, alu_ora, alu_and, alu_eor, alu_adc, alu_cmp, alu_sbc
						 );
	type alu_op is ( alu_ora, alu_and, alu_eor, alu_adc, alu_cmp, alu_sbc );
	
	type status_op is ( clear, set, dcare );
	type reg_status is array (5 downto 0) of status_op;
	
	type reg_mode is ( A_out, A_in, X_out, X_in, Y_out, Y_in  );
	
	type ram_mode is ( adr_out, adr_out_16, adr_in, adr_16_out, adr_16_out_16, adr_16_in );
end state;

package body state is
 
end state;
