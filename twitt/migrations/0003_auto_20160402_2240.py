# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitt', '0002_auto_20160402_0801'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set([('follower', 'following')]),
        ),
    ]
