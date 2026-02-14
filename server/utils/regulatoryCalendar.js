/**
 * Regulatory calendar for compliance deadlines and reporting periods
 */
class RegulatoryCalendar {
    constructor() {
        this.holidays = this._getSouthAfricanHolidays();
        this.deadlines = this.getRegulatoryDeadlines(new Date().getFullYear());
    }

    _getSouthAfricanHolidays() {
        // Fixed SA public holidays
        return [
            { month: 1, day: 1 },   // New Year's Day
            { month: 3, day: 21 },  // Human Rights Day
            { month: 4, day: 27 },  // Freedom Day
            { month: 5, day: 1 },   // Workers' Day
            { month: 6, day: 16 },  // Youth Day
            { month: 8, day: 9 },   // National Women's Day
            { month: 9, day: 24 },  // Heritage Day
            { month: 12, day: 16 }, // Day of Reconciliation
            { month: 12, day: 25 }, // Christmas Day
            { month: 12, day: 26 }  // Day of Goodwill
        ];
    }

    isHoliday(date) {
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return this.holidays.some(h => h.month === month && h.day === day);
    }

    isWeekend(date) {
        const day = date.getDay();
        return day === 0 || day === 6;
    }

    isBusinessDay(date) {
        return !this.isWeekend(date) && !this.isHoliday(date);
    }

    addBusinessDays(startDate, days) {
        const result = new Date(startDate);
        let remainingDays = days;
        
        while (remainingDays > 0) {
            result.setDate(result.getDate() + 1);
            if (this.isBusinessDay(result)) {
                remainingDays--;
            }
        }
        
        return result;
    }

    getQuarterDates(year) {
        return {
            Q1: { start: new Date(year, 0, 1), end: new Date(year, 2, 31) },
            Q2: { start: new Date(year, 3, 1), end: new Date(year, 5, 30) },
            Q3: { start: new Date(year, 6, 1), end: new Date(year, 8, 30) },
            Q4: { start: new Date(year, 9, 1), end: new Date(year, 11, 31) }
        };
    }

    getRegulatoryDeadlines(year) {
        return {
            // LPC annual returns due by 31 January
            lpcAnnualReturn: new Date(year, 0, 31),
            
            // FICA compliance reports due 30 April
            ficaCompliance: new Date(year, 3, 30),
            
            // POPIA annual audits due 30 June
            popiaAudit: new Date(year, 5, 30),
            
            // Trust account reconciliations due monthly
            monthlyReconciliation: Array.from({ length: 12 }, (_, i) => 
                this.addBusinessDays(new Date(year, i, 1), 15)
            )
        };
    }

    daysUntilDeadline(deadline) {
        const today = new Date();
        const diffTime = deadline - today;
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    // Initialize method - called by complianceEngine
    initialize() {
        this.deadlines = this.getRegulatoryDeadlines(new Date().getFullYear());
        return this;
    }
}

module.exports = { RegulatoryCalendar };
