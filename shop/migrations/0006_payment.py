import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_customer_email_alter_checkoutdetail_total_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('COD', 'Cash on Delivery'), ('CARD', 'Credit/Debit Card'), ('UPI', 'UPI'), ('NET_BANKING', 'Net Banking'), ('WALLET', 'Wallet')], max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='shop.order')),
            ],
        ),
    ]
