export interface Equipment {
  id: string
  name: string
  type: string
  size_category: string
  daily_rate: number
  active: boolean
}

export interface Booking {
  booking_id: string
  equipment_id: string
  contractor_name: string
  contractor_phone: string
  start_date: string
  end_date: string
  status: 'pending' | 'confirmed' | 'completed'
  created_at: string
  delivery_location: string | null
  total_amount: number | null
  deposit_amount: number | null
  balance_amount: number | null
  equipment?: { name: string } | null
}
