import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(OrderPaymentValidation.prototype, {
   shouldDownloadInvoice() {
        if (this.pos?.config?.disable_auto_invoice_download){
            return false;
        }
        return super.shouldDownloadInvoice();
    },
});
