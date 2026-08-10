"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";

export default function OverviewPage() {
  const { locale } = useI18nStore();
  const [wikiHtml, setWikiHtml] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadWiki() {
      setLoading(true);
      try {
        // Load language-appropriate wiki HTML
        const isZh = locale.startsWith("zh");
        const url = isZh
          ? "/wiki/smart-suite-wiki-zh.html"
          : "/wiki/smart-suite-wiki.html";
        const res = await fetch(url);
        if (res.ok) {
          const html = await res.text();
          setWikiHtml(html);
        }
      } catch {
        // Fallback
        setWikiHtml("");
      } finally {
        setLoading(false);
      }
    }
    loadWiki();
  }, [locale]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-[var(--text-muted)]">
        Loading...
      </div>
    );
  }

  if (!wikiHtml) {
    return (
      <div className="flex items-center justify-center h-64 text-[var(--text-muted)]">
        Overview page not found
      </div>
    );
  }

  return (
    <div
      className="overview-wiki-container"
      dangerouslySetInnerHTML={{ __html: wikiHtml }}
    />
  );
}
