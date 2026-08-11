"use client";

import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";

export default function ZhibuPage() {
  const router = useRouter();
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();

  const handleExport = () => {
    // Trigger download of zhibu_output.json
    window.open(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/zhibu/export?batch_id=${activeBatch}`,
      "_blank"
    );
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhibu.title")}</h1>
        <div className="flex items-center gap-3">
          <BatchSelector />
          <Button onClick={handleExport} variant="secondary" size="sm">
            {t("common.export")}
          </Button>
        </div>
      </div>

      <GlassCard>
        <div className="py-8 text-center text-[var(--text-muted)]">
          📤 Distribution content for <strong>{activeBatch}</strong> will load here.
          <br />
          <span className="text-xs">Endpoint: GET /api/zhibu/content?batch_id={activeBatch}</span>
        </div>
      </GlassCard>

      {/* CTA */}
      <div className="flex justify-end pt-4">
        <button onClick={() => router.push("/zhixi")} className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)] transition-colors">
          下一步：查看智析 →
        </button>
      </div>
    </div>
  );
}
