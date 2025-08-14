# Seeds demo data for testing
from db import init_db, SessionLocal
from models import Product, Ticket, RnDRecord, TrialRecord, ComplaintRecord

init_db()
db = SessionLocal()
try:
    # Products
    samples = [
        Product(lspl_grade="DieLube-3000", division="Die Casting", category="Die Lube", compatible_process="GDC", metal="Al", temp_min_c=200, temp_max_c=420, notes="High lubricity; low residue"),
        Product(lspl_grade="Flux-GR-10", division="Flux", category="Granular Flux", compatible_process="Melting/Holding", metal="Al", temp_min_c=650, temp_max_c=750, notes="Granular refining flux"),
        Product(lspl_grade="Forge-Lube-F1", division="Forging", category="Forging Lube", compatible_process="Hot forging", metal="Steel", temp_min_c=250, temp_max_c=500, notes="Graphite-based"),
        Product(lspl_grade="Plunger-XL", division="Die Casting", category="Plunger Lube", compatible_process="HPDC", metal="Al", temp_min_c=150, temp_max_c=400, notes="Extended tip life"),
        Product(lspl_grade="LadleCoat-RO", division="Foundry", category="Ladle Coat", compatible_process="Pouring", metal="Al", temp_min_c=650, temp_max_c=750, notes="RO water recommended"),
    ]
    db.add_all(samples)

    # R&D
    db.add_all([
        RnDRecord(lspl_grade="DieLube-3000", spec_summary="Stable film at 350-420C", flags="low-residue;fast-wetting", constraints="Water hardness < 120 ppm; RO/DM preferred"),
        RnDRecord(lspl_grade="Flux-GR-10", spec_summary="Improves melt cleanliness", flags="granular", constraints="Use at 0.2%-0.5% of melt"),
    ])

    # Trials
    db.add_all([
        TrialRecord(customer_name="Alpha Castings", lspl_grade="DieLube-3000", conditions="GDC Al 420C die temp", outcome="success", notes="Reduced soldering"),
        TrialRecord(customer_name="Bravo Foundry", lspl_grade="Flux-GR-10", conditions="650-720C", outcome="success", notes="Cleaner metal"),
        TrialRecord(customer_name="SteelForge Ltd", lspl_grade="Forge-Lube-F1", conditions="Die 300C", outcome="mixed", notes="Improved die life but smoke"),
    ])

    # Complaints
    db.add_all([
        ComplaintRecord(customer_name="Alpha Castings", lspl_grade="Plunger-XL", conditions="HPDC", issue="Residue build-up", severity="low"),
    ])

    # Tickets (history)
    db.add_all([
        Ticket(ticket_id="T-1001", division="Die Casting", category="Die Lube", requirement_details="Al GDC, die temp 380-400C, RO water", proposed_grade="DieLube-3000", proposed_reason="Past success at similar temps", customer_name="Alpha Castings", priority="High"),
        Ticket(ticket_id="T-1002", division="Flux", category="Granular Flux", requirement_details="Melting 680C, AA6082", proposed_grade="Flux-GR-10", proposed_reason="Cleanliness improvement", customer_name="Bravo Foundry", priority="Medium"),
    ])

    db.commit()
    print("Seeded demo data.")
finally:
    db.close()
