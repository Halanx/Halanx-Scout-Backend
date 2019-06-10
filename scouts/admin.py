from django.contrib import admin

from scouts.models import ScoutPermanentAddress, ScoutBankDetail, ScoutWallet, ScoutWorkAddress, ScoutPicture, Scout, \
    ScoutPayment, ScoutDocument, ScoutNotificationCategory, ScoutNotification


class ScoutPermanentAddressInline(admin.StackedInline):
    model = ScoutPermanentAddress


class ScoutWorkAddressInline(admin.StackedInline):
    model = ScoutWorkAddress


class ScoutBankDetailInline(admin.StackedInline):
    model = ScoutBankDetail


class ScoutWalletInline(admin.StackedInline):
    model = ScoutWallet


class ScoutPictureTabular(admin.TabularInline):
    model = ScoutPicture
    extra = 0
    ordering = ('-timestamp',)


class ScoutDocumentInline(admin.TabularInline):
    model = ScoutDocument
    extra = 0
    ordering = ('-timestamp',)


@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_profile_pic_html',)
    readonly_fields = ('get_profile_pic_html',)
    raw_id_fields = ('user', )
    inlines = (
        ScoutPermanentAddressInline,
        ScoutWorkAddressInline,
        ScoutBankDetailInline,
        ScoutWalletInline,
        ScoutPictureTabular,
        ScoutDocumentInline,
    )

    def get_inline_instances(self, request, obj=None):
        # Return no inlines when obj is being created
        if not obj:
            return []
        else:
            return super(ScoutAdmin, self).get_inline_instances(request, obj)


@admin.register(ScoutPayment)
class ScoutPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'amount', 'status', 'due_date', 'paid_on')
    raw_id_fields = ('wallet', )


@admin.register(ScoutWallet)
class ScoutWalletAdmin(admin.ModelAdmin):
    pass


@admin.register(ScoutNotificationCategory)
class ScoutNotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_notification_category_image_html')
    readonly_fields = ('get_notification_category_image_html', )


@admin.register(ScoutNotification)
class ScoutNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'scout', 'category', 'content', 'get_notification_image_html', )
    search_fields = ('scout__first_name', 'scout__phone_no', )
    list_filter = ('category', )
