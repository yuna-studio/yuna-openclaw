"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { LayoutDashboard, History, Leaf } from "lucide-react";
import { Heartbeat } from "./heartbeat";

export const GNB = () => {
  const pathname = usePathname();

  const navItems = [
    { name: "대시보드", href: "/", icon: LayoutDashboard },
    { name: "연대기", href: "/timeline", icon: History },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-5 bg-ghibli-bg/80 backdrop-blur-md border-b-2 border-ghibli-accent/10">
      <div className="flex items-center gap-10">
        <Link href="/" className="flex items-center gap-3">
          <motion.div 
            whileHover={{ rotate: 15 }}
            className="w-10 h-10 rounded-xl bg-ghibli-accent flex items-center justify-center shadow-lg"
          >
            <Leaf className="text-ghibli-bg" size={24} fill="currentColor" />
          </motion.div>
          <div className="flex flex-col">
            <span className="font-bold text-lg leading-none text-ghibli-text">가재 컴퍼니</span>
            <span className="text-[10px] font-mono tracking-widest text-ghibli-accent font-bold uppercase">Sanctuary</span>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <div className={`relative px-5 py-2.5 rounded-full transition-all flex items-center gap-2 group ${isActive ? 'text-ghibli-text font-bold' : 'text-slate-500 hover:text-ghibli-text'}`}>
                  <item.icon size={18} className={isActive ? 'text-ghibli-accent' : ''} />
                  <span className="text-sm">{item.name}</span>
                  {isActive && (
                    <motion.div 
                      layoutId="nav-active"
                      className="absolute inset-0 bg-ghibli-accent/5 rounded-full border-2 border-ghibli-accent/20"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden md:flex flex-col items-end mr-4">
            <span className="text-[10px] font-bold text-ghibli-accent uppercase tracking-tighter">System Health</span>
            <span className="text-xs font-bold text-ghibli-text">무결성 100%</span>
        </div>
        <Heartbeat />
      </div>
    </nav>
  );
};
