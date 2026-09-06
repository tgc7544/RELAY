import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { WebShell } from './components/WebShell'
import { Home } from './screens/Home'
import { Browse } from './screens/Browse'
import { Booking } from './screens/Booking'
import { Confirmed } from './screens/Confirmed'
import { Owner } from './screens/Owner'
import { BookingsList } from './screens/BookingsList'
import { Profile } from './screens/Profile'
import { TrackDelivery } from './screens/TrackDelivery'

export default function App() {
  return (
    <BrowserRouter>
      <WebShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/equipment" element={<Browse />} />
          <Route path="/booking/:equipmentId" element={<Booking />} />
          <Route path="/confirmed/:bookingId" element={<Confirmed />} />
          <Route path="/owner" element={<Owner />} />
          <Route path="/bookings" element={<BookingsList />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/track/:bookingId" element={<TrackDelivery />} />
        </Routes>
      </WebShell>
    </BrowserRouter>
  )
}
