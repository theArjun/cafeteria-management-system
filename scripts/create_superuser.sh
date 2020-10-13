script="
from django.contrib.auth import get_user_model;
email = 'admin@example.com';
username = 'admin';
password = 'pass';
User = get_user_model();
if User.objects.filter(username=username).count()==0:
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell