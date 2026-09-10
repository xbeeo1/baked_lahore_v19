/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TopVendors extends Component {
    static template = "cno_baked_custom_dashboard.TopVendors";

    setup() {
        this.orm = useService("orm");

        const today = this.getToday();

        this.state = useState({
            date_from: today,
            date_to: today,
            vendor_search: "",
            vendors: [],
            loading: false,
        });

        onWillStart(() => this.loadVendors());
    }

    getToday() {
        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    async loadVendors() {
        if (!this.state.date_from || !this.state.date_to) {
            return;
        }

        this.state.loading = true;

        try {
            this.state.vendors = await this.orm.call(
                "report.pos.order",
                "get_top_vendors",
                [],
                {
                    date_from: this.state.date_from,
                    date_to: this.state.date_to,
                    vendor_search: this.state.vendor_search,
                }
            );
        } finally {
            this.state.loading = false;
        }
    }

    async onDateChange() {
        if (this.state.date_from > this.state.date_to) {
            return;
        }

        await this.loadVendors();
    }

    async onRefresh() {
        await this.loadVendors();
    }

    async onVendorSearch() {
        await this.loadVendors();
    }

    async onVendorKeydown(ev) {
        if (ev.key === "Enter") {
            await this.onVendorSearch();
        }
    }

    formatRevenue(value) {
        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value || 0);
    }
}

registry
    .category("actions")
    .add("top_vendor_action", TopVendors);