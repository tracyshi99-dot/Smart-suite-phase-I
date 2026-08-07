import { ArrowRight, BookOpen, Search, PenTool, Sparkles, Package, BarChart3 } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="p-8 max-w-5xl">
      {/* Hero */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-text-primary mb-3">
          Smart Suite <span className="text-amazon-orange">GEO</span> Content Platform
        </h1>
        <p className="text-text-secondary text-base max-w-2xl">
          AI 驱动的 GEO 内容自动化生产工具，让 Amazon 品牌内容被 AI 搜索引擎主动引用和推荐
        </p>
      </div>

      {/* Situation Guide (inspired by Protozoa) */}
      <div className="mb-10">
        <p className="text-xs uppercase tracking-wider text-text-muted mb-2 font-semibold">
          选择您当前的情况
        </p>
        <h2 className="text-xl font-bold text-text-primary mb-6">
          先了解 GEO 流程，还是直接开始操作？
        </h2>

        {/* Step cards (Protozoa style) */}
        <div className="bg-surface-dark rounded-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-6 h-6 bg-amazon-orange/20 rounded-full flex items-center justify-center">
              <span className="text-amazon-orange text-xs font-bold">○</span>
            </div>
            <h3 className="text-white font-semibold">先了解 GEO 内容流水线</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FlowCard num="A" title="检索短语是什么" desc="了解 AI 搜索引擎用户的真实检索行为" />
            <FlowCard num="B" title="内容怎么优化" desc="SEO + GEO 双优化标准，提升 AI 引用率" />
            <FlowCard num="C" title="怎么衡量效果" desc="品牌提及率、链接覆盖率、BPS 对比大盘" />
          </div>
        </div>
      </div>

      {/* Action Cards (numbered, Protozoa style) */}
      <h3 className="flex items-center gap-2 text-base font-semibold mb-4">
        <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center">
          <span className="text-text-muted text-xs font-bold">▶</span>
        </div>
        直接开始操作
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ActionCard
          num="01"
          title="生成检索短语"
          desc="输入核心词根，AI 自动裂变为 15-40 字的自然问句"
          tag="智库"
          tagColor="orange"
          href="/zhiku"
          hints={["输入词根一键裂变", "支持中/英/繁體/韩/越", "自动评分和分类"]}
        />
        <ActionCard
          num="02"
          title="验证 AI 覆盖"
          desc="在 7 个 AI 搜索引擎中验证短语是否被亚马逊内容覆盖"
          tag="智测"
          tagColor="green"
          href="/zhice"
          hints={["DeepSeek/千问/ChatGPT/Gemini", "品牌提及 + 官网链接检测", "自动发现内容 Gap"]}
        />
        <ActionCard
          num="03"
          title="产出 GEO 内容"
          desc="基于知识库生成 SEO+GEO 双优化的文章，合规审查"
          tag="智造"
          tagColor="blue"
          href="/zhizao"
          hints={["800-1500字结构化文章", "自动合规审查 + 敏感词检测", "三段式模型架构"]}
        />
        <ActionCard
          num="04"
          title="追踪效果"
          desc="查看 GEO 对 Reg Start 的贡献、品牌提及率趋势"
          tag="智析"
          tagColor="purple"
          href="/zhixi"
          hints={["646条短语×7平台追踪", "月度 BPS 对比大盘", "品牌提及率 / 链接覆盖率"]}
        />
      </div>
    </div>
  );
}

function FlowCard({ num, title, desc }: { num: string; title: string; desc: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4 flex items-start gap-3">
      <span className="w-6 h-6 bg-amazon-orange rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
        {num}
      </span>
      <div>
        <p className="text-white text-sm font-medium">{title}</p>
        <p className="text-white/50 text-xs mt-0.5">{desc}</p>
      </div>
    </div>
  );
}

function ActionCard({
  num, title, desc, tag, tagColor, href, hints,
}: {
  num: string; title: string; desc: string; tag: string;
  tagColor: string; href: string; hints: string[];
}) {
  const tagClass = {
    orange: "tag-orange",
    green: "tag-green",
    blue: "tag-blue",
    purple: "tag-purple",
  }[tagColor] || "tag-orange";

  return (
    <Link href={href} className="card p-6 group cursor-pointer block">
      <div className="flex items-start justify-between mb-3">
        <span className="step-number">{num}</span>
        <span className={tagClass}>{tag}</span>
      </div>
      <h3 className="font-bold text-base text-text-primary mb-1.5 group-hover:text-amazon-orange transition-colors">
        {title}
      </h3>
      <p className="text-text-secondary text-sm mb-4">{desc}</p>
      <ul className="space-y-1.5">
        {hints.map((h, i) => (
          <li key={i} className="text-xs text-text-muted flex items-center gap-1.5">
            <span className="w-1 h-1 bg-amazon-orange/40 rounded-full" />
            {h}
          </li>
        ))}
      </ul>
      <div className="mt-4 flex items-center gap-1 text-sm font-medium text-amazon-orange opacity-0 group-hover:opacity-100 transition-opacity">
        开始操作 <ArrowRight size={14} />
      </div>
    </Link>
  );
}
