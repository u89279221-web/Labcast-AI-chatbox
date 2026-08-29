"""
Seed script to populate the database with demo machines.
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, SQLModel
from app.models.machine import Machine
from app.core.database import engine as default_engine

from app.models.user import User
from app.core.security import get_password_hash

def seed_database(engine):
    """
    Seed the database with 3 realistic demo machines.
    """
    SQLModel.metadata.create_all(engine)
    
    machines = [
        Machine(
            id="CNC01",
            name="HAAS VF-2 CNC Milling Machine",
            sop=[
                "Ensure work area is clean and all safety guards are in place.",
                "Load raw material into the vise and secure tightly.",
                "Load correct tool into the spindle or tool magazine.",
                "Load G-code program via USB or network.",
                "Perform a dry run (cutting air) to verify the toolpath.",
                "Close the doors, engage coolant, and start the cutting cycle."
            ],
            safety_text="Always wear safety glasses when operating the CNC machine. Do not wear loose clothing, jewelry, or open-toed shoes. Never open the doors while the spindle is spinning or axis is moving. Ensure emergency stop buttons are accessible before starting.",
            emergency=False,
            manual_text="""# HAAS VF-2 CNC Milling Machine Operator Manual

## Operation Overview
The HAAS VF-2 is a 3-axis CNC vertical milling center used for precision machining of metals and plastics. It utilizes G-code instructions to move the spindle across X, Y, and Z axes. The machine features a 30-horsepower spindle, a 20-pocket tool changer, and a flood coolant system. Before operating, always ensure the machine is homed, the tool offsets are correctly set, and the workpiece is securely clamped.

## Safety Protocols
Safety is paramount when working with the VF-2. Operators must wear ANSI-approved safety glasses at all times. Loose hair must be tied back, and gloves should NOT be worn near the rotating spindle to prevent entanglement. The interlocked doors are designed to prevent the machine from running high-speed operations when open; never bypass these interlocks. Keep the enclosure clear of tools, measuring instruments, and debris before initiating a cycle. 

## Emergency Shutdown Procedure
In the event of a tool crash, fire, or other critical failure:
1. Immediately press the large red EMERGENCY STOP (E-STOP) button located on the front control panel.
2. If a fire occurs, do not open the machine doors to prevent oxygen from feeding the fire. Use the shop's designated CO2 extinguisher through the side access port if safe to do so.
3. Once the machine has come to a complete halt, power off the main breaker switch located on the rear electrical cabinet.
4. Notify the laboratory supervisor immediately and do not attempt to clear the jam or restart the machine without authorization."""
        ),
        Machine(
            id="LATHE02",
            name="South Bend Precision Manual Lathe",
            sop=[
                "Check oil levels in the headstock and apron.",
                "Secure the workpiece in the chuck, ensuring no more than 3 times the diameter extends unsupported.",
                "Select and secure the proper cutting tool in the tool post.",
                "Set the correct spindle speed and feed rate for the material.",
                "Manually rotate the chuck to ensure everything clears the carriage.",
                "Turn on the spindle and slowly engage the tool to make the cut."
            ],
            safety_text="Wear safety glasses. NEVER leave the chuck key in the chuck. Keep hands, rags, and brushes away from rotating parts. Do not wear long sleeves, ties, or gloves while operating the lathe.",
            emergency=False,
            manual_text="""# South Bend Precision Manual Lathe Operator Manual

## Operation Overview
The South Bend Lathe is a manual metalworking lathe used for turning, facing, drilling, and threading cylindrical parts. The operator controls the carriage, cross-slide, and compound rest manually or via power feeds to shape the rotating workpiece. It features a geared headstock for selecting precise RPMs and a quick-change gearbox for threading and feeding. Proper lubrication of the ways and gears is required daily before operation.

## Safety Protocols
Lathes pose severe entanglement hazards. Never wear gloves, loose clothing, jewelry, or long hair down while operating. The most critical safety rule is to NEVER leave the chuck key inside the chuck, even for a moment; it can become a lethal projectile if the machine is turned on. Always stop the spindle completely before taking measurements, adjusting the tool, or clearing chips. Use a chip hook or brush to remove swarf, not your hands.

## Emergency Shutdown Procedure
If the workpiece comes loose, a tool breaks, or entanglement occurs:
1. Immediately pull down the main power clutch/brake lever (usually located near the apron or above the headstock) to stop the spindle rotation.
2. Hit the red EMERGENCY STOP button on the electrical control box if the mechanical brake fails.
3. Step back from the machine until all moving parts have completely stopped.
4. Turn off the main rotary disconnect switch to isolate power.
5. Report the incident to the shop manager. Do not attempt to re-chuck a damaged part without inspection."""
        ),
        Machine(
            id="LASER03",
            name="Epilog Fusion Pro 48 Laser Cutter",
            sop=[
                "Turn on the main power and wait for the system to initialize.",
                "Turn on the exhaust fan and air assist compressor.",
                "Place the material on the cutting bed and focus the laser manually or using autofocus.",
                "Send the artwork file from the computer to the laser dashboard.",
                "Select the correct power, speed, and frequency settings for the material.",
                "Press the start button on the machine panel and monitor the cutting process."
            ],
            safety_text="Never leave the laser cutter unattended while it is running. Only cut approved materials (e.g., acrylic, wood). Do NOT cut PVC or vinyl, as they release toxic and corrosive chlorine gas. Keep the lid closed during operation.",
            emergency=False,
            manual_text="""# Epilog Fusion Pro 48 Laser Cutter Operator Manual

## Operation Overview
The Epilog Fusion Pro 48 is a CO2 laser engraving and cutting system with a 48" x 36" work area. It uses a high-powered invisible infrared beam to vaporize material. The machine requires a dedicated exhaust system to remove fumes and an air assist compressor to blow away debris and prevent flaming. It can cut wood, acrylic, leather, and cardboard, but operators must verify that any new material does not contain PVC or toxic halogens before processing. 

## Safety Protocols
Fire is the primary hazard when operating the laser cutter. The machine must never be left unattended during a cutting or engraving cycle. Even a small flare-up can quickly turn into an uncontrollable fire if not extinguished. The lid is made of specialized safety glass that blocks the CO2 laser wavelength; never operate the machine if the lid is cracked or if the interlock switches have been tampered with. Ensure the exhaust system is running properly before starting to prevent toxic fume buildup in the lab.

## Emergency Shutdown Procedure
In the event of a sustained fire inside the cabinet or a software runaway:
1. Immediately press the EMERGENCY STOP button on the front right of the machine, or open the top lid to break the interlock and instantly cut power to the laser tube.
2. If a fire continues burning after the laser is off, do NOT open the lid completely, as oxygen will fuel the flames.
3. Use a Halotron or CO2 fire extinguisher through a small opening to extinguish the fire. Do NOT use a dry chemical or water extinguisher as it will destroy the precision optics and electronics.
4. Turn off the exhaust fan to prevent sucking flames into the ductwork.
5. Evacuate the area if the fire cannot be contained and pull the building fire alarm."""
        )
    ]
    
    with Session(engine) as session:
        for machine in machines:
            # Upsert or check if exists to avoid errors on multiple runs
            existing = session.get(Machine, machine.id)
            if not existing:
                session.add(machine)
            else:
                existing.name = machine.name
                existing.sop = machine.sop
                existing.safety_text = machine.safety_text
                existing.manual_text = machine.manual_text
        session.commit()

        users = [
            User(id='U1', email='admin@labcast.edu', hashed_password=get_password_hash('admin123'), role='admin'),
            User(id='U2', email='faculty@labcast.edu', hashed_password=get_password_hash('faculty123'), role='faculty'),
            User(id='U3', email='tech@labcast.edu', hashed_password=get_password_hash('tech123'), role='technician'),
            User(id='U4', email='student@labcast.edu', hashed_password=get_password_hash('student123'), role='student')
        ]
        for u in users:
            if not session.get(User, u.id):
                session.add(u)
        session.commit()
    print("Database seeded successfully with 3 demo machines.")

if __name__ == "__main__":
    seed_database(default_engine)

