from django.contrib import admin

from scouts.models import ScoutPermanentAddress, ScoutBankDetail, ScoutWallet, ScoutWorkAddress, ScoutPicture, Scout, \
    ScoutPayment


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


@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_profile_pic_html',)
    readonly_fields = ('get_profile_pic_html',)
    inlines = (
        ScoutPermanentAddressInline,
        ScoutWorkAddressInline,
        ScoutBankDetailInline,
        ScoutWalletInline,
        ScoutPictureTabular,
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
