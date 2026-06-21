import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_rename_feature_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='date_added',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_bestseller',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_trending',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(db_index=True, default=10),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['-date_added', 'is_featured', 'is_bestseller'], name='product_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_deleted'], name='product_category_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['seller', 'is_deleted'], name='product_seller_idx'),
        ),
    ]
