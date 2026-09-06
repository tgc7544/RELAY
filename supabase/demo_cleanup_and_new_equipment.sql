-- Run this whole file in the Supabase SQL Editor.
--
-- 1) Lets the app's anon key delete bookings (needed so the demo can clean
--    up test bookings itself going forward). Safe to re-run.
drop policy if exists "Public can delete bookings" on bookings;
create policy "Public can delete bookings"
on bookings for delete
to anon
using (true);

-- 2) Clear all bookings — every row in the table at the time of this
--    request was test data.
delete from bookings;

-- 3) Add the new excavator listing. Run as postgres here (not through the
--    anon key) on purpose: equipment listings should only ever be added
--    through a trusted path (this editor, or a future owner/admin flow),
--    never by the public anon key the client apps use — otherwise anyone
--    could insert fake listings into the live catalog.
--
--    The id is fixed rather than left to gen_random_uuid() because the
--    app derives each listing's displayed parish deterministically from
--    its id (there's no location column yet) — this specific id hashes to
--    "St. Philip" in that function, so the card will show the right parish.
insert into equipment (id, name, type, size_category, daily_rate, active)
values (
  '91c757ad-d9ae-4307-9ae1-a1709e41ed54',
  'Clarke 20-Ton Excavator',
  'excavator',
  'large',
  850.00,
  true
);

-- Verification — check these two results in the output pane.
select count(*) as remaining_bookings from bookings;
select id, name, daily_rate, active from equipment where name = 'Clarke 20-Ton Excavator';
