from django.db import models


class Property(models.Model):
    TYPE_CHOICES = [
        ("2bed", "2 Bedroom Flat"),
        ("1bed", "1 Bedroom Studio"),
        ("self-con", "Self-Con Apartment"),
        ("duplex", "Duplex"),
        ("mini-flat", "Mini Flat"),
        ("bungalow", "Bungalow"),
    ]
    landlord = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="properties"
    )
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    price_per_year = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    sqft = models.PositiveIntegerField(null=True, blank=True)
    age = models.CharField(max_length=20, default="New")
    description = models.TextField()
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="property_images/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} — {self.location}"

    @property
    def display_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        if self.image:
            return self.image.url
        return self.image_url or "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=600"

    @property
    def primary_image(self):
        return self.display_image


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="property_images/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.property.title}"


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name


class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="amenities")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Property Amenities"

    def __str__(self):
        return f"{self.property} — {self.amenity}"


class PropertyReview(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="property_reviews")
    rating = models.PositiveSmallIntegerField()  # 1–5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("property", "reviewer")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reviewer} → {self.property.title} ({self.rating}★)"
