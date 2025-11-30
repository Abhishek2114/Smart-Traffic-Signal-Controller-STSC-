# Smart Traffic Signal Controller Assembly Code
# RV32I subset for traffic control logic

.global _start

_start:
    # Initialize registers
    addi x1, x0, 0      # x1 = 0 (return address)
    addi x2, x0, 30     # x2 = 30 (green light duration)
    addi x3, x0, 0      # x3 = 0 (sensor data)
    addi x4, x0, 5      # x4 = 5 (yellow light duration)
    addi x5, x0, 0      # x5 = 0 (temp)

    # Read sensor data
    lw x5, 0(x0)        # Load sensor data from memory[0]

    # Check if traffic present
    beq x5, x0, no_traffic  # If no traffic, skip to no_traffic

    # Traffic present: set green light
    sw x2, 4(x0)        # Store green duration to control register

    # Delay for green light
    jal delay

    # Set yellow light
    sw x4, 8(x0)        # Store yellow duration

    # Delay for yellow
    jal delay

no_traffic:
    # Set red light (default)
    addi x6, x0, 60     # Red duration
    sw x6, 12(x0)       # Store red duration

    # Loop back for next cycle
    j _start

delay:
    addi x6, x0, 1000   # Delay counter
delay_loop:
    addi x6, x6, -1     # Decrement counter
    bne x6, x0, delay_loop  # Loop until zero
    jalr x0, 0(x1)      # Return
