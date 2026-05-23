import unittest
from datetime import datetime

# ==========================================
# BUSINESS LOGIC FUNCTION
# (Extracted here just for testing purposes)
# ==========================================
def calculate_rental_cost(daily_rate, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    days = (end_date - start_date).days

    if days <= 0:
        return 0  # Invalid booking length

    return days * daily_rate

# ==========================================
# AUTOMATED UNIT TESTS
# ==========================================
class TestFleetLogic(unittest.TestCase):

    def test_normal_booking_math(self):
        # Testing a standard 5-day rental at $100/day
        cost = calculate_rental_cost(100.0, '2026-06-01', '2026-06-06')
        self.assertEqual(cost, 500.0, "5 days at $100 should be $500")

    def test_invalid_same_day_booking(self):
        # Testing that users cannot pick the exact same day for start and end
        cost = calculate_rental_cost(100.0, '2026-06-01', '2026-06-01')
        self.assertEqual(cost, 0, "Same day bookings should return 0 cost")

    def test_invalid_past_end_date(self):
        # Testing that users cannot make the end date happen before the start date
        cost = calculate_rental_cost(150.0, '2026-06-10', '2026-06-01')
        self.assertEqual(cost, 0, "Negative days should return 0 cost")

if __name__ == '__main__':
    unittest.main()