from django.contrib import admin
from ttsapp.models import Userkeys, Uploads
import csv
from django.http import HttpResponse


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class UploadsAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('user', 'file_name', 'is_processed', 'created_on')
    list_filter = ('user', 'is_active', 'is_processed')
    search_fields = ['user__email', 'user__first_name', 'file_name']
    ordering = ['-created_on']
    actions = ["export_as_csv"]


class UserkeysAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('user', 'api_key', 'created_on')
    list_filter = ('user',)
    search_fields = ['user__email', 'user__first_name']
    ordering = ['-created_on']
    actions = ["export_as_csv"]


admin.site.register(Uploads, UploadsAdmin)
admin.site.register(Userkeys, UserkeysAdmin)
admin.site.disable_action('delete_selected')

