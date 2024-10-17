from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Manejaro creación del usuario, Django tiene un por defecto, este usa eso por defecto y lo mejora
class UserAccountManager(BaseUserManager):
    #Funcion crear usuario con email
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
# Funcion crear super usuario
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

#Cuando se llaman a los objetos por ejemplo User.objects se obtienen dichos objetos, entonces con userAccountManager, se hace para que sigan dicha logica
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self): 
        return f"{self.first_name} {self.last_name}"


    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True 

    def __str__(self):
        return f"{self.email}"
