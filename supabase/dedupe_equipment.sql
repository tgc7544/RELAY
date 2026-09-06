-- Removes the duplicate equipment rows left over from seed.sql having been
-- run twice (once before the "Public can view equipment" policy existed,
-- once after). For each (name, type, size_category, daily_rate) group,
-- keeps the oldest row (lowest ctid) and deletes the rest — but only rows
-- with no booking pointing at them, so this can never break a real booking
-- via the equipment_id foreign key.

delete from equipment e
where e.ctid <> (
  select min(e2.ctid)
  from equipment e2
  where e2.name = e.name
    and e2.type = e.type
    and e2.size_category = e.size_category
    and e2.daily_rate = e.daily_rate
)
and not exists (
  select 1 from bookings b where b.equipment_id = e.id
);

-- Verification — should read 17 with no duplicate names.
select count(*) as equipment_row_count from equipment;
select name, count(*) from equipment group by name having count(*) > 1;
