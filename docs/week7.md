# Week 7: Architecture Integration

During Week 7 (Sep 8 - Sep 14), we began integrating our standalone hardware tests and web apps into a cohesive software architecture.

## Accomplishments
- **CNC Controller**: Built the `stepper_motor_controller` Flask app and the underlying Arduino logic to handle web-based 3-axis control.
- **Remote Tooling**: Implemented `ssh_cmd.py`, `sync.py`, and `monitor_viewer.py` to seamlessly deploy code to our remote Uno Q board.
- **Hardware Finalization**: Produced the first versions of our finalized `.stl` files for the physical structure of the bot.

Deprecated tests, temporary Streamlit apps, and intermediate deployment scripts from Week 7/8 are archived in [reference/week7_8/](../reference/week7_8/). All finalized tooling is stored in `code/`.
