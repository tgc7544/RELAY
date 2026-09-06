-- Combined, idempotent fix for the mobile app demo. Safe to run multiple
-- times — drops/recreates policies instead of erroring if they exist, and
-- only seeds equipment if the table is actually empty. Run this whole file
-- in the Supabase SQL Editor (Project > SQL Editor > New query > Run),
-- then look at the two SELECT results at the bottom of the output pane.

-- 1) Policies: allow the mobile app's anon key to read equipment and to
--    read/create bookings. RLS is enabled with no policies by default
--    (correct for the WhatsApp backend, which uses service_role and
--    bypasses RLS) — these open exactly what the browser client needs.
drop policy if exists "Public can view equipment" on equipment;
create policy "Public can view equipment"
on equipment for select
to anon
using (true);

drop policy if exists "Public can create bookings" on bookings;
create policy "Public can create bookings"
on bookings for insert
to anon
with check (true);

drop policy if exists "Public can view bookings" on bookings;
create policy "Public can view bookings"
on bookings for select
to anon
using (true);

-- 2) Seed equipment, only if the table is currently empty (won't duplicate
--    rows if you already have data from a prior partial run).
insert into equipment (name, type, size_category, daily_rate)
select * from (values
    ('Mini Excavator 2T',        'excavator',      'mini',     180.00),
    ('Midi Excavator 6T',        'excavator',      'midi',     320.00),
    ('Standard Excavator 15T',   'excavator',      'standard', 550.00),
    ('Single-Axle Dump Truck',   'dump_truck',     'small',    250.00),
    ('Tandem-Axle Dump Truck',   'dump_truck',     'mid',      400.00),
    ('Tri-Axle Dump Truck',      'dump_truck',     'large',    600.00),
    ('Mobile Mini Crane',        'crane',          'mini',     700.00),
    ('Spider Crawler Crane',     'crane',          'compact',  900.00),
    ('Scissor Lift 26ft',        'scissor_lift',   'standard', 150.00),
    ('Boom Lift 45ft',           'boom_lift',      'standard', 280.00),
    ('Portable Concrete Mixer',  'concrete_mixer', 'small',    60.00),
    ('Mid-Size Concrete Mixer',  'concrete_mixer', 'mid',      140.00),
    ('Generator 20kVA',          'generator',      'standard', 120.00),
    ('Generator 60kVA',          'generator',      'large',    260.00),
    ('Tube-and-Clamp Scaffolding','scaffolding',   'standard', 90.00),
    ('Plate Compactor',          'compactor',      'standard', 70.00),
    ('Water Pump 4-inch',        'water_pump',     'standard', 55.00)
) as v(name, type, size_category, daily_rate)
where not exists (select 1 from equipment);

-- 3) Verification — check these two results in the output pane.
select count(*) as equipment_row_count from equipment;
select policyname, cmd, roles from pg_policies where tablename in ('equipment', 'bookings');
