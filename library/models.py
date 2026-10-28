from django.db import models
from django.contrib.auth.models import User
import datetime

class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. MED-TXT")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Book Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()


class Book(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Low Stock', 'Low Stock'),
        ('Borrowed Out', 'Borrowed Out'),
        ('Archived', 'Archived'),
    )

    book_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. BK-1001")
    isbn = models.CharField(max_length=30, blank=True, null=True, help_text="ISBN-10 or ISBN-13")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    category_name = models.CharField(max_length=100, blank=True, null=True, help_text="Fallback category")
    publisher = models.CharField(max_length=200, blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True, default="1st Edition")
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Rack A - Row 3")
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='books/', blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True, help_text="Reliable image fallback")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author} ({self.book_id or 'BK'})"

    def save(self, *args, **kwargs):
        if self.category and not self.category_name:
            self.category_name = self.category.name

        if self.available_copies == 0:
            self.status = 'Borrowed Out'
        elif self.available_copies < 2:
            self.status = 'Low Stock'
        else:
            self.status = 'Available'

        super().save(*args, **kwargs)
        if not self.book_id:
            self.book_id = f"BK-{self.pk:04d}"
            Book.objects.filter(pk=self.pk).update(book_id=self.book_id)

    @property
    def get_cover(self):
        if self.cover_image:
            return self.cover_image.url
        elif self.cover_url:
            return self.cover_url
        return 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=80'


class LibraryMember(models.Model):
    MEMBER_TYPES = (
        ('Student', 'Student'),
        ('Doctor', 'Doctor'),
        ('Faculty', 'Faculty'),
        ('Staff', 'Staff'),
        ('Member', 'General Member'),
    )

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
    )

    member_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. STU-001 or MEM-101")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_member')
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='Student')
    department = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Medicine, Nursing, Cardiology")
    address = models.TextField(blank=True, null=True)
    max_allowed_books = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    joined_date = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.member_id or 'MEM'}) - {self.member_type}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.member_id:
            prefix = "STU" if self.member_type == 'Student' else "MEM"
            self.member_id = f"{prefix}-{self.pk:04d}"
            LibraryMember.objects.filter(pk=self.pk).update(member_id=self.member_id)

    @property
    def active_borrow_count(self):
        return self.borrow_records.filter(status__in=['Issued', 'Overdue']).count()


class BookIssue(models.Model):
    STATUS_CHOICES = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
        ('Lost', 'Lost'),
    )

    issue_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. ISS-001")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='borrow_records')
    issue_date = models.DateField(default=datetime.date.today)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"Issue #{self.issue_id or self.pk}: {self.book.title} to {self.member.name}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = datetime.date.today() + datetime.timedelta(days=14)

        if not self.return_date and datetime.date.today() > self.due_date and self.status == 'Issued':
            self.status = 'Overdue'
            days_overdue = (datetime.date.today() - self.due_date).days
            self.fine_amount = days_overdue * 5.0  # $5 or Rs.5 per day

        super().save(*args, **kwargs)
        if not self.issue_id:
            self.issue_id = f"ISS-{self.pk:04d}"
            BookIssue.objects.filter(pk=self.pk).update(issue_id=self.issue_id)

    @property
    def is_overdue(self):
        return not self.return_date and datetime.date.today() > self.due_date
