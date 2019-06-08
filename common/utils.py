from utility.random_utils import generate_random_code

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


def get_notification_category_image_upload_path(instance, filename):
    return "notification-category-images/{}/{}-{}".format(instance.id, generate_random_code(n=5),
                                                          filename.split('/')[-1])
