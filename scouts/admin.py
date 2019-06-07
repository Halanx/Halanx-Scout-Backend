from django.contrib import admin

from scouts.models import ScoutPermanentAddress, ScoutBankDetail, ScoutWallet, ScoutWorkAddress, ScoutPicture, Scout, \
    ScoutPayment, ScoutDocument


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


@admin.register(ScoutWallet)
class ScoutWalletAdmin(admin.ModelAdmin):
    pass
