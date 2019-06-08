DocumentTypeCategories = (
    ('Aadhar', 'Aadhar'),
    ('PAN', 'PAN'),
)


PAID = "paid"
PENDING = "pending"
CANCELLED = "cancelled"

PaymentStatusCategories = (
    (PAID, "Paid"),
    (PENDING, "Pending"),
    (CANCELLED, "Cancelled")
)


WITHDRAWAL = "withdrawal"
DEPOSIT = "deposit"

PaymentTypeCategories = (
    (WITHDRAWAL, "Withdrawal"),
    (DEPOSIT, "Deposit")
)


DATETIME_SERIALIZER_FORMAT = '%d %B %Y %I:%M %p'
