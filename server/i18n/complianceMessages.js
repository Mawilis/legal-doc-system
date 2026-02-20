/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ COMPLIANCE MESSAGES - INVESTOR-GRADE ● FORENSIC ● PRODUCTION                ║
  ║ FICA Compliant | POPIA Compliant | Multi-lingual | Legal Grade             ║
  ║ Version: 1.0.0 - Production - Complete i18n System                          ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

class ComplianceMessages {
    constructor() {
        this.messages = new Map();
        this.supportedLocales = ['en-US', 'en-ZA', 'af-ZA', 'xh-ZA', 'zu-ZA', 'fr-FR', 'pt-PT', 'de-DE', 'es-ES', 'zh-CN', 'ar-SA'];
        this.defaultLocale = 'en-ZA'; // South African English as default for legal compliance
        this.fallbackLocale = 'en-US'; // US English as fallback
        this.loaded = false;
        this.loadMessages();
    }

    /**
     * Load all message files
     */
    loadMessages() {
        try {
            const localesDir = path.join(__dirname, 'locales');
            
            // Load each locale file
            this.supportedLocales.forEach(locale => {
                const filePath = path.join(localesDir, `${locale}.json`);
                if (fs.existsSync(filePath)) {
                    const messages = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                    this.messages.set(locale, messages);
                    logger.info(`✅ Loaded compliance messages for locale: ${locale}`);
                } else {
                    logger.warn(`⚠️ Missing message file for locale: ${locale}`);
                    // Create default file if missing
                    this.createDefaultLocaleFile(locale);
                }
            });
            
            this.loaded = true;
        } catch (error) {
            logger.error('❌ Failed to load compliance messages:', error);
            throw error;
        }
    }

    /**
     * Create default locale file if missing
     */
    createDefaultLocaleFile(locale) {
        const defaultMessages = this.getDefaultMessages(locale);
        const filePath = path.join(__dirname, 'locales', `${locale}.json`);
        fs.writeFileSync(filePath, JSON.stringify(defaultMessages, null, 2), 'utf8');
        this.messages.set(locale, defaultMessages);
        logger.info(`📝 Created default message file for locale: ${locale}`);
    }

    /**
     * Get message by key and locale
     */
    getMessage(key, locale = this.defaultLocale, params = {}) {
        // Try requested locale
        let messages = this.messages.get(locale);
        
        // Fallback to default locale if not found
        if (!messages) {
            messages = this.messages.get(this.defaultLocale);
        }
        
        // Fallback to English if still not found
        if (!messages) {
            messages = this.messages.get('en-US');
        }
        
        // Get message by key (support dot notation)
        const value = this._getNestedValue(messages, key);
        
        if (!value) {
            logger.warn(`⚠️ Missing message key: ${key} for locale: ${locale}`);
            return `[${key}]`;
        }
        
        // Replace parameters
        return this._replaceParams(value, params);
    }

    /**
     * Get nested value using dot notation
     */
    _getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : undefined;
        }, obj);
    }

    /**
     * Replace parameters in message
     */
    _replaceParams(message, params) {
        if (!params || Object.keys(params).length === 0) return message;
        
        return message.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }

    /**
     * Get all messages for locale
     */
    getAllMessages(locale = this.defaultLocale) {
        return this.messages.get(locale) || this.messages.get(this.defaultLocale) || {};
    }

    /**
     * Get supported locales
     */
    getSupportedLocales() {
        return this.supportedLocales;
    }

    /**
     * Check if locale is supported
     */
    isLocaleSupported(locale) {
        return this.supportedLocales.includes(locale);
    }

    /**
     * Get default messages structure
     */
    getDefaultMessages(locale) {
        // Return appropriate default messages based on locale
        const language = locale.split('-')[0];
        
        const baseMessages = {
            "common": {
                "yes": "Yes",
                "no": "No",
                "continue": "Continue",
                "cancel": "Cancel",
                "save": "Save",
                "delete": "Delete",
                "edit": "Edit",
                "view": "View",
                "download": "Download",
                "upload": "Upload",
                "search": "Search",
                "filter": "Filter",
                "clear": "Clear",
                "loading": "Loading...",
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "info": "Information",
                "confirm": "Confirm",
                "back": "Back",
                "next": "Next",
                "finish": "Finish",
                "submit": "Submit"
            },
            "validation": {
                "required": "This field is required",
                "email": "Please enter a valid email address",
                "phone": "Please enter a valid phone number",
                "idNumber": "Please enter a valid ID number",
                "passport": "Please enter a valid passport number",
                "date": "Please enter a valid date",
                "minLength": "Must be at least {{min}} characters",
                "maxLength": "Must be no more than {{max}} characters",
                "min": "Must be at least {{min}}",
                "max": "Must be no more than {{max}}",
                "match": "Fields do not match",
                "unique": "This value must be unique",
                "invalid": "Invalid value"
            },
            "fica": {
                "title": "FICA Compliance",
                "required": "FICA verification is required by law",
                "consent": "I consent to FICA verification",
                "status": {
                    "pending": "FICA verification pending",
                    "inProgress": "FICA verification in progress",
                    "approved": "FICA verification approved",
                    "rejected": "FICA verification rejected",
                    "escalated": "FICA verification escalated"
                },
                "messages": {
                    "approved": "Your FICA verification has been approved. Reference: {{reference}}",
                    "rejected": "Your FICA verification has been rejected. Reason: {{reason}}",
                    "additionalInfo": "Additional information required for FICA verification",
                    "expired": "FICA verification has expired. Please renew."
                },
                "documents": {
                    "idCopy": "ID Copy",
                    "proofOfAddress": "Proof of Address",
                    "proofOfIncome": "Proof of Income",
                    "companyRegistration": "Company Registration",
                    "taxClearance": "Tax Clearance",
                    "directorIdCopies": "Director ID Copies"
                }
            },
            "popia": {
                "title": "POPIA Compliance",
                "consent": "I consent to the processing of my personal information",
                "privacyPolicy": "Privacy Policy",
                "termsOfUse": "Terms of Use",
                "dataRights": "My Data Rights",
                "messages": {
                    "consentRequired": "Your consent is required under POPIA",
                    "consentGranted": "Thank you for providing your consent",
                    "consentWithdrawn": "Your consent has been withdrawn",
                    "dataAccess": "Request access to your data",
                    "dataCorrection": "Request correction of your data",
                    "dataDeletion": "Request deletion of your data"
                }
            },
            "onboarding": {
                "title": "Client Onboarding",
                "stages": {
                    "initiated": "Onboarding Initiated",
                    "clientInfo": "Client Information",
                    "ficaScreening": "FICA Screening",
                    "documentUpload": "Document Upload",
                    "documentVerification": "Document Verification",
                    "review": "Legal Review",
                    "completed": "Onboarding Completed"
                },
                "status": {
                    "pending": "Pending",
                    "inProgress": "In Progress",
                    "completed": "Completed",
                    "cancelled": "Cancelled",
                    "rejected": "Rejected"
                },
                "messages": {
                    "welcome": "Welcome to client onboarding",
                    "started": "Onboarding process started",
                    "completed": "Onboarding completed successfully",
                    "cancelled": "Onboarding cancelled",
                    "rejected": "Onboarding rejected"
                }
            },
            "errors": {
                "generic": "An error occurred. Please try again.",
                "notFound": "Resource not found",
                "unauthorized": "Unauthorized access",
                "forbidden": "Access forbidden",
                "validation": "Validation error",
                "server": "Server error",
                "timeout": "Request timeout",
                "network": "Network error",
                "database": "Database error",
                "fileUpload": "File upload error",
                "fileSize": "File size exceeds limit",
                "fileType": "File type not supported"
            },
            "notifications": {
                "email": {
                    "welcome": {
                        "subject": "Welcome to Wilsy OS",
                        "body": "Dear {{name}},\n\nWelcome to Wilsy OS. Your onboarding has been initiated.\n\nYour reference number: {{reference}}\n\nThank you for choosing Wilsy OS."
                    },
                    "ficaApproved": {
                        "subject": "FICA Verification Approved",
                        "body": "Dear {{name}},\n\nYour FICA verification has been approved.\n\nReference: {{reference}}\n\nThank you for your cooperation."
                    },
                    "ficaRejected": {
                        "subject": "FICA Verification Rejected",
                        "body": "Dear {{name}},\n\nYour FICA verification has been rejected.\n\nReason: {{reason}}\n\nPlease provide additional information."
                    },
                    "onboardingCompleted": {
                        "subject": "Onboarding Completed",
                        "body": "Dear {{name}},\n\nYour onboarding has been successfully completed.\n\nYou can now access all Wilsy OS features.\n\nThank you for choosing Wilsy OS."
                    }
                },
                "sms": {
                    "welcome": "Welcome to Wilsy OS. Your reference: {{reference}}",
                    "ficaApproved": "FICA approved. Reference: {{reference}}",
                    "ficaRejected": "FICA rejected: {{reason}}",
                    "onboardingCompleted": "Onboarding complete. Welcome!"
                }
            },
            "legal": {
                "disclaimer": "This is a legal document. Please read carefully.",
                "acknowledgment": "I acknowledge that I have read and understood",
                "signature": "Signature",
                "date": "Date",
                "witness": "Witness",
                "jurisdiction": "Jurisdiction: South Africa",
                "governingLaw": "Governing Law: Laws of the Republic of South Africa",
                "disputeResolution": "Dispute Resolution: Arbitration in terms of the Arbitration Act",
                "indemnity": "Indemnity",
                "warranty": "Warranty",
                "confidentiality": "Confidentiality Agreement"
            },
            "audit": {
                "created": "Record created",
                "updated": "Record updated",
                "deleted": "Record deleted",
                "viewed": "Record viewed",
                "exported": "Record exported",
                "verified": "Record verified",
                "rejected": "Record rejected",
                "approved": "Record approved",
                "escalated": "Record escalated"
            }
        };

        // Customize based on language
        switch(language) {
            case 'af':
                return this.getAfrikaansMessages(baseMessages);
            case 'xh':
                return this.getXhosaMessages(baseMessages);
            case 'zu':
                return this.getZuluMessages(baseMessages);
            case 'fr':
                return this.getFrenchMessages(baseMessages);
            case 'pt':
                return this.getPortugueseMessages(baseMessages);
            case 'de':
                return this.getGermanMessages(baseMessages);
            case 'es':
                return this.getSpanishMessages(baseMessages);
            case 'zh':
                return this.getChineseMessages(baseMessages);
            case 'ar':
                return this.getArabicMessages(baseMessages);
            default:
                return baseMessages;
        }
    }

    // Language-specific message overrides
    getAfrikaansMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Ja",
                no: "Nee",
                continue: "Gaan voort",
                cancel: "Kanselleer",
                save: "Stoor",
                delete: "Verwyder",
                edit: "Wysig",
                view: "Bekyk",
                download: "Laai af",
                upload: "Laai op",
                search: "Soek",
                filter: "Filtreer",
                loading: "Laai...",
                success: "Sukses",
                error: "Fout",
                warning: "Waarskuwing",
                info: "Inligting"
            },
            fica: {
                ...base.fica,
                title: "FICA Nakoming",
                consent: "Ek stem in tot FICA-verifikasie"
            },
            popia: {
                ...base.popia,
                title: "POPIA Nakoming",
                consent: "Ek stem in tot die verwerking van my persoonlike inligting"
            }
        };
    }

    getXhosaMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Ewe",
                no: "Hayi",
                continue: "Qhubeka",
                cancel: "Rhoxisa",
                save: "Gcina",
                delete: "Cima",
                edit: "Hlela",
                view: "Jonga",
                download: "Khuphela",
                upload: "Faka",
                search: "Khangela",
                loading: "Iyalayisha..."
            }
        };
    }

    getZuluMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Yebo",
                no: "Cha",
                continue: "Qhubeka",
                cancel: "Khansela",
                save: "Londoloza",
                delete: "Susa",
                edit: "Hlela",
                view: "Buka",
                download: "Landa",
                upload: "Layisha",
                search: "Cinga",
                loading: "Iyalayisha..."
            }
        };
    }

    getFrenchMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Oui",
                no: "Non",
                continue: "Continuer",
                cancel: "Annuler",
                save: "Enregistrer",
                delete: "Supprimer",
                edit: "Modifier",
                view: "Voir",
                download: "Télécharger",
                upload: "Téléverser",
                search: "Rechercher",
                loading: "Chargement..."
            }
        };
    }

    getPortugueseMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Sim",
                no: "Não",
                continue: "Continuar",
                cancel: "Cancelar",
                save: "Salvar",
                delete: "Excluir",
                edit: "Editar",
                view: "Visualizar",
                download: "Baixar",
                upload: "Carregar",
                search: "Pesquisar",
                loading: "Carregando..."
            }
        };
    }

    getGermanMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Ja",
                no: "Nein",
                continue: "Fortfahren",
                cancel: "Abbrechen",
                save: "Speichern",
                delete: "Löschen",
                edit: "Bearbeiten",
                view: "Ansehen",
                download: "Herunterladen",
                upload: "Hochladen",
                search: "Suchen",
                loading: "Laden..."
            }
        };
    }

    getSpanishMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "Sí",
                no: "No",
                continue: "Continuar",
                cancel: "Cancelar",
                save: "Guardar",
                delete: "Eliminar",
                edit: "Editar",
                view: "Ver",
                download: "Descargar",
                upload: "Subir",
                search: "Buscar",
                loading: "Cargando..."
            }
        };
    }

    getChineseMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "是",
                no: "否",
                continue: "继续",
                cancel: "取消",
                save: "保存",
                delete: "删除",
                edit: "编辑",
                view: "查看",
                download: "下载",
                upload: "上传",
                search: "搜索",
                loading: "加载中..."
            }
        };
    }

    getArabicMessages(base) {
        return {
            ...base,
            common: {
                ...base.common,
                yes: "نعم",
                no: "لا",
                continue: "استمر",
                cancel: "إلغاء",
                save: "حفظ",
                delete: "حذف",
                edit: "تعديل",
                view: "عرض",
                download: "تحميل",
                upload: "رفع",
                search: "بحث",
                loading: "جاري التحميل..."
            }
        };
    }
}

// Singleton instance
module.exports = new ComplianceMessages();
