-- Run this in the Supabase SQL Editor (Project > SQL Editor > New query).

create extension if not exists pgcrypto;

create table if not exists equipment (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    type text not null,
    size_category text not null,
    daily_rate numeric(10, 2) not null,
    active boolean not null default true
);

create table if not exists bookings (
    booking_id uuid primary key default gen_random_uuid(),
    equipment_id uuid not null references equipment(id),
    contractor_name text not null,
    contractor_phone text not null,
    start_date date not null,
    end_date date not null,
    status text not null default 'pending' check (status in ('pending', 'confirmed', 'completed')),
    created_at timestamptz not null default now(),
    constraint valid_date_range check (end_date >= start_date)
);

create index if not exists bookings_equipment_id_idx on bookings (equipment_id);
create index if not exists bookings_date_range_idx on bookings (start_date, end_date);

-- Who gets notified when a deposit lands on this item.
alter table equipment add column if not exists owner_phone text;

-- Payment fields: snapshotted at booking time so later equipment rate changes
-- never retroactively alter an existing booking's deposit/balance math.
alter table bookings add column if not exists delivery_location text;
alter table bookings add column if not exists total_amount numeric(10, 2);
alter table bookings add column if not exists deposit_amount numeric(10, 2);
alter table bookings add column if not exists balance_amount numeric(10, 2);

-- Payment state is tracked separately from `status` (the booking lifecycle:
-- pending/confirmed/completed) rather than overloading it with a "paid"
-- value — a booking can be confirmed-but-unpaid or completed-but-unpaid,
-- so these need to vary independently of the lifecycle field.
alter table bookings add column if not exists deposit_paid boolean not null default false;
alter table bookings add column if not exists deposit_paid_at timestamptz;
alter table bookings add column if not exists balance_paid boolean not null default false;
alter table bookings add column if not exists balance_paid_at timestamptz;

create table if not exists conversations (
    id bigint generated always as identity primary key,
    phone_number text not null,
    role text not null check (role in ('user', 'assistant')),
    message text not null,
    created_at timestamptz not null default now()
);

create index if not exists conversations_phone_created_idx on conversations (phone_number, created_at);

-- The app talks to Supabase with the service_role key (bypasses RLS), so RLS
-- here is defense in depth: it blocks anon/authenticated keys from touching
-- these tables outright, in case one is ever exposed client-side.
alter table equipment enable row level security;
alter table bookings enable row level security;
alter table conversations enable row level security;
