import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { Locale, Translations } from './types';
import { en } from './locales/en';
import { de } from './locales/de';

export * from './types';

const TRANSLATIONS: Record<Locale, Translations> = {
  en,
  de,
};

interface I18nContextValue {
  locale: Locale;
  /** Single source of truth for the German check. Derive nothing locally. */
  isGerman: boolean;
  setLocale: (locale: Locale) => void;
  t: Translations;
  formatDate: (date: Date | string | number, options?: Intl.DateTimeFormatOptions) => string;
  formatTime: (date: Date | string | number) => string;
  formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

const STORAGE_KEY = 'timonelo_locale';

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<Locale>(() => {
    // 1. Check URL query param ?lang=de or ?lang=en
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const urlLang = urlParams.get('lang')?.toLowerCase();
      if (urlLang === 'de' || urlLang === 'en') {
        return urlLang;
      }

      // 2. Check localStorage
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'de' || saved === 'en') {
        return saved;
      }

      // 3. Check browser navigator language
      if (navigator.language?.startsWith('de')) {
        return 'de';
      }
    }
    return 'en';
  });

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, newLocale);
      document.documentElement.lang = newLocale;
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  const value = useMemo<I18nContextValue>(() => {
    const t = TRANSLATIONS[locale] || TRANSLATIONS.en;

    const formatDate = (date: Date | string | number, options?: Intl.DateTimeFormatOptions) => {
      const d = typeof date === 'object' ? date : new Date(date);
      return new Intl.DateTimeFormat(locale === 'de' ? 'de-DE' : 'en-GB', {
        dateStyle: 'medium',
        ...options,
      }).format(d);
    };

    const formatTime = (date: Date | string | number) => {
      const d = typeof date === 'object' ? date : new Date(date);
      return new Intl.DateTimeFormat(locale === 'de' ? 'de-DE' : 'en-GB', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }).format(d);
    };

    const formatNumber = (num: number, options?: Intl.NumberFormatOptions) => {
      return new Intl.NumberFormat(locale === 'de' ? 'de-DE' : 'en-GB', options).format(num);
    };

    return {
      locale,
      isGerman: locale === 'de',
      setLocale,
      t,
      formatDate,
      formatTime,
      formatNumber,
    };
  }, [locale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export const useI18n = (): I18nContextValue => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within a LanguageProvider');
  }
  return context;
};
