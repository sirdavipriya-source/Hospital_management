from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="e.g. CARD-01")
    description = models.TextField()
    image = models.ImageField(upload_to='departments/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Fallback reliable remote URL for realistic UI")
    icon_class = models.CharField(max_length=50, default='fa-clinic-medical', help_text="Font Awesome icon class e.g. fa-heartbeat")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def doctor_count(self):
        return self.doctors.filter(is_available=True).count()

    @property
    def specialization_count(self):
        return self.specializations.filter(is_active=True).count()

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80'


class Specialization(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True, null=True, help_text="e.g. SPEC-CRD-01")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='specializations')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'department')

    def __str__(self):
        return f"{self.name} ({self.department.name})"

