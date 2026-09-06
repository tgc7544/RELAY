-- Run this in the Supabase SQL Editor (Project > SQL Editor > New query).
--
-- The mobile app talks to Supabase directly from the browser with the anon
-- key (see mobile-app/.env). schema.sql enables RLS on equipment/bookings
-- with no policies, which is correct for the WhatsApp backend (it uses the
-- service_role key and bypasses RLS) but blocks the anon key entirely.
-- These policies open the exact two operations the mobile demo needs:
-- public read of equipment, and public creation of bookings.

create policy "Public can view equipment"
on equipment for select
to anon
using (true);

create policy "Public can create bookings"
on bookings for insert
to anon
with check (true);

create policy "Public can view bookings"
on bookings for select
to anon
using (true);
