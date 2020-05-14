from django.db import models
#from webcam.fields import CameraField

class Owner(models.Model):
    STUDENT = 'ST'
    TEACHER = 'TE'
    STAFF = 'SA'
    OWNER_TYPE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (STAFF, 'Staff'),

    ]
    owner_type = models.CharField(
        max_length=2,
        choices=OWNER_TYPE_CHOICES,
        default=STUDENT,
    )
    owner_first_name = models.CharField(max_length=100)
    owner_last_name= models.CharField(max_length=100)
    department= models.CharField(max_length=100)
    phone_number = models.CharField(max_length=50)
    owner_id = models.CharField(max_length=50)
    image = models.ImageField(null=True, upload_to='owner_image',)
    #image = CameraField('CameraPictureField', format='jpeg', null=True, blank=True, upload_to='owner_image')

    def __str__(self):
        return f'{self.owner_first_name}[phone={self.phone_number}]'

class Laptop(models.Model):
    laptop_name = models.CharField(max_length=50)
    laptop_model = models.CharField(max_length=50)
    serial_number= models.CharField(max_length=50)
    laptop_color = models.CharField(max_length=50)
    owner = models.ForeignKey(Owner, null=True, related_name='laptops', on_delete=models.CASCADE)
    qr_code = models.ImageField(blank=True, null=True, upload_to='qr_code_images')


