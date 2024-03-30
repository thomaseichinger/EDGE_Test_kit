# EDGE_Test_kit
Exit conditions:

Timer: This condition is implemented using a loop that checks the elapsed time against the specified duration. When the elapsed time exceeds the specified duration, the loop breaks, and the test step exits.

Battery Voltage Conditions (Bat Voltage>= and Bat Voltage<): These conditions are implemented within loops that continuously query the battery voltage of each PCU. The loop continues until the average battery voltage across all PCUs meets the specified condition.

Battery State of Charge (SOC) Conditions (SOC> and SOC<): Similar to the battery voltage conditions, these conditions are implemented within loops that continuously query the battery state of charge of each PCU. The loop continues until the average battery state of charge across all PCUs meets the specified condition.