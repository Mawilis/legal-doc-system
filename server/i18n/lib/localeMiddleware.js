/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ LOCALE MIDDLEWARE - INVESTOR-GRADE MODULE                                   ║
  ║ Automatic locale detection | Tenant-specific defaults                       ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/i18n/lib/localeMiddleware.js
 */

'use strict';

const i18nService = require('./i18nService');
const logger = require('../../utils/logger');

class LocaleMiddleware {
    constructor() {
        this.supportedLocales = [];
        this.defaultLocale = 'en-ZA';
    }

    /**
     * Initialize with supported locales
     */
    initialize() {
        this.supportedLocales = i18nService.getSupportedLocales();
        logger.info(`LocaleMiddleware initialized with ${this.supportedLocales.length} locales`);
    }

    /**
     * Express middleware to set locale based on request
     */
    middleware() {
        return (req, res, next) => {
            try {
                // Determine locale (priority order)
                const locale = this.determineLocale(req);
                
                // Attach i18n methods to request
                req.i18n = {
                    locale,
                    t: (key, params) => i18nService.t(key, locale, params),
                    legalTerm: (term) => i18nService.legalTerm(term, locale),
                    formatDate: (date, options) => i18nService.formatDate(date, locale, options),
                    formatNumber: (num, options) => i18nService.formatNumber(num, locale, options),
                    formatCurrency: (amount, currency) => i18nService.formatCurrency(amount, currency, locale),
                    direction: i18nService.getDirection(locale),
                    isRTL: i18nService.isRTL(locale)
                };
                
                // Set response locals for views
                res.locals.i18n = req.i18n;
                res.locals.locale = locale;
                
                // Set Content-Language header
                res.setHeader('Content-Language', locale);
                
                next();
            } catch (error) {
                logger.error('Locale middleware error:', error);
                next();
            }
        };
    }

    /**
     * Determine locale from request
     */
    determineLocale(req) {
        // 1. Check query parameter
        if (req.query.lang && this.isSupported(req.query.lang)) {
            return req.query.lang;
        }
        
        // 2. Check cookie
        if (req.cookies && req.cookies.locale && this.isSupported(req.cookies.locale)) {
            return req.cookies.locale;
        }
        
        // 3. Check session
        if (req.session && req.session.locale && this.isSupported(req.session.locale)) {
            return req.session.locale;
        }
        
        // 4. Check Accept-Language header
        const acceptLanguage = req.headers['accept-language'];
        if (acceptLanguage) {
            const preferred = this.parseAcceptLanguage(acceptLanguage);
            if (preferred && this.isSupported(preferred)) {
                return preferred;
            }
        }
        
        // 5. Default
        return this.defaultLocale;
    }

    /**
     * Parse Accept-Language header
     */
    parseAcceptLanguage(header) {
        if (!header) return null;
        
        const languages = header.split(',')
            .map(lang => {
                const [locale, quality = 'q=1'] = lang.split(';');
                const q = parseFloat(quality.split('=')[1]) || 1;
                return { locale: locale.trim(), quality: q };
            })
            .sort((a, b) => b.quality - a.quality);
        
        return languages[0]?.locale;
    }

    /**
     * Check if locale is supported
     */
    isSupported(locale) {
        if (!this.supportedLocales || this.supportedLocales.length === 0) {
            this.supportedLocales = i18nService.getSupportedLocales();
        }
        return this.supportedLocales.includes(locale);
    }

    /**
     * Create locale switcher component
     */
    localeSwitcher(currentLocale) {
        if (!this.supportedLocales || this.supportedLocales.length === 0) {
            this.supportedLocales = i18nService.getSupportedLocales();
        }
        
        const locales = [
            { code: 'en-ZA', name: 'English (SA)', flag: '🇿🇦' },
            { code: 'af-ZA', name: 'Afrikaans', flag: '🇿🇦' },
            { code: 'nr-ZA', name: 'isiNdebele', flag: '🇿🇦' },
            { code: 'nso-ZA', name: 'Sepedi', flag: '🇿🇦' },
            { code: 'st-ZA', name: 'Sesotho', flag: '🇿🇦' },
            { code: 'ss-ZA', name: 'SiSwati', flag: '🇿🇦' },
            { code: 'tn-ZA', name: 'Setswana', flag: '🇿🇦' },
            { code: 'ts-ZA', name: 'Xitsonga', flag: '🇿🇦' },
            { code: 've-ZA', name: 'Tshivenda', flag: '🇿🇦' },
            { code: 'xh-ZA', name: 'isiXhosa', flag: '🇿🇦' },
            { code: 'zu-ZA', name: 'isiZulu', flag: '🇿🇦' },
            { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
            { code: 'de-DE', name: 'Deutsch', flag: '🇩🇪' },
            { code: 'fr-FR', name: 'Français', flag: '🇫🇷' },
            { code: 'es-ES', name: 'Español', flag: '🇪🇸' },
            { code: 'pt-PT', name: 'Português', flag: '🇵🇹' },
            { code: 'ar-SA', name: 'العربية', flag: '🇸🇦' },
            { code: 'zh-CN', name: '中文', flag: '🇨🇳' }
        ];
        
        return locales
            .filter(l => this.supportedLocales.includes(l.code))
            .map(l => ({
                ...l,
                current: l.code === currentLocale
            }));
    }

    /**
     * Generate HTML for locale switcher
     */
    localeSwitcherHTML(currentLocale) {
        const locales = this.localeSwitcher(currentLocale);
        
        if (locales.length === 0) {
            return '';
        }
        
        return `
<div class="locale-switcher">
    <select onchange="window.location.href=this.value">
        ${locales.map(l => `
            <option value="?lang=${l.code}" ${l.current ? 'selected' : ''}>
                ${l.flag} ${l.name}
            </option>
        `).join('')}
    </select>
</div>
        `.trim();
    }
}

module.exports = new LocaleMiddleware();
