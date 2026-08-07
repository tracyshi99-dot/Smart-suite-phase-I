"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen, Search, PenTool, Sparkles, Package,
  BarChart3, Brain, Settings
} from "lucide-react";

const navItems = [
  { href: "/zhiku", label: "智库", sublabel: "Phrase Discovery", icon: BookOpen },
  { href: "/zhice", label: "智测", sublabel: "Gap Verification", icon: Search },
  { href: "/zhizao", label: "智造", sublabel: "Content Production", icon: PenTool },
  { href: "/zhiyou", label: "智优", sublabel: "Optimization", icon: Sparkles },
  { href: "/zhibu", label: "智布", sublabel: "Publishing", icon: Package },
  { href: "/zhixi", label: "智析", sublabel: "Analytics", icon: BarChart3 },
  { href: "/zhongshu", label: "智中枢", sublabel: "Orchestrator", icon: Brain },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-amazon-dark flex flex-col shadow-sidebar z-50">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-amazon-orange rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-base">Smart Suite</h1>
            <p className="text-white/40 text-xs">GEO Content Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${isActive ? "sidebar-link-active" : ""}`}
            >
              <Icon size={18} />
              <div>
                <span className="block">{item.label}</span>
                <span className="block text-xs opacity-50">{item.sublabel}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-white/10">
        <Link href="/settings" className="sidebar-link">
          <Settings size={18} />
          <span>Settings</span>
        </Link>
        <div className="mt-3 px-4">
          <p className="text-white/30 text-xs">v2.0 · Phase II</p>
        </div>
      </div>
    </aside>
  );
}
