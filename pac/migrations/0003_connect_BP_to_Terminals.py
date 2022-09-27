from django.db import migrations, models, connection
import django.db.models.deletion


class Migration(migrations.Migration):
    def apply_circular_fk(apps, schema_editor):
        cursor_update = connection.cursor()
        apply_fk = """ALTER TABLE [dbo].[BasingPoint]  WITH NOCHECK ADD  CONSTRAINT [BasingPoint_Terminal_FK] FOREIGN KEY([DefaultTerminalID])
                      REFERENCES [dbo].[Terminal] ([TerminalID])
                      ON DELETE CASCADE """
        cursor_update.execute(apply_fk)

    dependencies = [
        ('pac', '0002_auto_20220922_1556'),
    ]

    operations = [
        migrations.RunPython(apply_circular_fk),
    ]
