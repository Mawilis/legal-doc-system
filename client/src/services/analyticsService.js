// client/src/services/analyticsService.js

export const trackEvent = (eventCategory, eventAction, eventLabel) => {
    if (window.gtag) {
        window.gtag('event', eventAction, {
            event_category: eventCategory,
            event_label: eventLabel,
        });
    }
};

export const trackPageView = (pageTitle) => {
    if (window.gtag) {
        window.gtag('config', 'YOUR_GOOGLE_ANALYTICS_ID', {
            page_title: pageTitle,
            page_location: window.location.href,
        });
    }
};
