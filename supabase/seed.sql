-- Sample inventory for local testing. Run ONLY against a fresh/empty
-- equipment table — re-running this against already-seeded data creates
-- duplicate rows (this has happened before; see app/db.py history).
-- `type` values match what app/agent.py's tool definitions expect.

insert into equipment (name, type, size_category, daily_rate, owner_phone) values
    ('Mini Excavator 2T',        'excavator',      'mini',     180.00, '+14164508497'),
    ('Midi Excavator 6T',        'excavator',      'midi',     320.00, '+14164508497'),
    ('Standard Excavator 15T',   'excavator',      'standard', 550.00, '+14164508497'),
    ('Single-Axle Dump Truck',   'dump_truck',     'small',    250.00, '+14164508497'),
    ('Tandem-Axle Dump Truck',   'dump_truck',     'mid',      400.00, '+14164508497'),
    ('Tri-Axle Dump Truck',      'dump_truck',     'large',    600.00, '+14164508497'),
    ('Mobile Mini Crane',        'crane',          'mini',     700.00, '+14164508497'),
    ('Spider Crawler Crane',     'crane',          'compact',  900.00, '+14164508497'),
    ('Scissor Lift 26ft',        'scissor_lift',   'standard', 150.00, '+14164508497'),
    ('Boom Lift 45ft',           'boom_lift',      'standard', 280.00, '+14164508497'),
    ('Portable Concrete Mixer',  'concrete_mixer', 'small',    60.00,  '+14164508497'),
    ('Mid-Size Concrete Mixer',  'concrete_mixer', 'mid',      140.00, '+14164508497'),
    ('Generator 20kVA',          'generator',      'standard', 120.00, '+14164508497'),
    ('Generator 60kVA',          'generator',      'large',    260.00, '+14164508497'),
    ('Tube-and-Clamp Scaffolding','scaffolding',   'standard', 90.00,  '+14164508497'),
    ('Plate Compactor',          'compactor',      'standard', 70.00,  '+14164508497'),
    ('Water Pump 4-inch',        'water_pump',     'standard', 55.00,  '+14164508497');
