import {
  Construction,
  Truck,
  Forklift,
  ArrowUpDown,
  MoveUp,
  Barrel,
  Zap,
  LayoutGrid,
  Weight,
  Droplets,
  type LucideIcon,
} from 'lucide-react'

export const CATEGORY_CHIPS = ['All', 'Excavators', 'Trucks', 'Generators', 'Lifts', 'Mixers'] as const
export type CategoryChip = (typeof CATEGORY_CHIPS)[number]

const CHIP_TYPE_MAP: Record<CategoryChip, string[]> = {
  All: [],
  Excavators: ['excavator'],
  Trucks: ['dump_truck'],
  Generators: ['generator'],
  Lifts: ['scissor_lift', 'boom_lift'],
  Mixers: ['concrete_mixer'],
}

export function matchesChip(type: string, chip: CategoryChip): boolean {
  if (chip === 'All') return true
  return CHIP_TYPE_MAP[chip].includes(type)
}

const TYPE_ICONS: Record<string, LucideIcon> = {
  excavator: Construction,
  dump_truck: Truck,
  crane: Forklift,
  scissor_lift: ArrowUpDown,
  boom_lift: MoveUp,
  concrete_mixer: Barrel,
  generator: Zap,
  scaffolding: LayoutGrid,
  compactor: Weight,
  water_pump: Droplets,
}

export function iconForType(type: string): LucideIcon {
  return TYPE_ICONS[type] ?? Construction
}

const PHOTO_TYPES = new Set([
  'excavator',
  'dump_truck',
  'crane',
  'scissor_lift',
  'boom_lift',
  'concrete_mixer',
  'generator',
  'scaffolding',
  'compactor',
  'water_pump',
])

export function photoForType(type: string): string {
  const key = PHOTO_TYPES.has(type) ? type : 'excavator'
  return `/equipment/${key}.jpg`
}

export function typeLabel(value: string): string {
  return value
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ')
}

const PARISHES = [
  'Christ Church',
  'St. Michael',
  'St. James',
  'St. Peter',
  'St. Lucy',
  'St. Andrew',
  'St. Joseph',
  'St. John',
  'St. Philip',
  'St. George',
  'St. Thomas',
]

export function parishFor(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0
  return PARISHES[hash % PARISHES.length]
}
