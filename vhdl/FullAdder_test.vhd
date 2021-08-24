LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
ENTITY FullAdder_test IS
END FullAdder_test;
 
ARCHITECTURE behavior OF FullAdder_test IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT FullAdder
    PORT(
         x : IN  std_logic;
         y : IN  std_logic;
         cin : IN  std_logic;
         s : OUT  std_logic;
         c : OUT  std_logic
        );
    END COMPONENT;
    

   --Inputs
   signal x : std_logic := '0';
   signal y : std_logic := '0';
   signal cin : std_logic := '0';

 	--Outputs
   signal s : std_logic;
   signal c : std_logic;
   -- No clocks detected in port list. Replace <clock> below with 
   -- appropriate port name 
 
BEGIN
 
	-- Instantiate the Unit Under Test (UUT)
   uut: FullAdder PORT MAP (
          x => x,
          y => y,
          cin => cin,
          s => s,
          c => c
        );

   -- Stimulus process
   stim_proc: process
   begin		
      -- hold reset state for 100 ns.
      wait for 100 ns;	

      -- insert stimulus here
		
		x <= '0' after 100 ns,
			  '1' after 140 ns;
		
		y <= '0' after 100 ns,
			  '1' after 120 ns,
			  '0' after 140 ns,
			  '1' after 160 ns;
			 
		cin <= '0' after 100 ns,
				 '1' after 110 ns,
				 '0' after 120 ns,
				 '1' after 130 ns,
				 '0' after 140 ns,
				 '1' after 150 ns,
				 '0' after 160 ns,
				 '1' after 170 ns;

      wait;
   end process;

END;
