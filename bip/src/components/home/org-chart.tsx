"use client";

import Image from "next/image";
import { motion } from "framer-motion";

const TEAM = [
  {
    name: "낭만코딩",
    role: "CEO",
    image: "/profile-nangman.jpg",
    color: "border-primary",
    twitter: "romantic_coding",
  },
  {
    name: "비서가재 🦞",
    role: "총괄",
    image: "/profile-secretary.jpg",
    color: "border-secondary",
  },
  {
    name: "탐정가재 🔍",
    role: "실무",
    image: "/profile-scout.jpg",
    color: "border-accent-highlight",
  },
  {
    name: "판사가재 ⚖️",
    role: "검수",
    image: "/profile-judge.jpg",
    color: "border-text-primary",
  },
];

export function OrgChart() {
  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      {/* 헤드 카피 */}
      <div className="text-center mb-12">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          1명의 사람과 3마리의 가재.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/50 leading-snug"
        >
          그게 우리 팀 전부예요.
        </motion.p>
      </div>

      {/* 팀원 카드 */}
      <div className="grid grid-cols-4 gap-3">
        {TEAM.map((member, i) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08 }}
            className="flex flex-col items-center text-center"
          >
            <div className={`relative w-16 h-16 rounded-full overflow-hidden border-[3px] ${member.color} shadow-md mb-2`}>
              <Image
                src={member.image}
                alt={member.name}
                fill
                className="object-cover"
              />
            </div>
            <p className="text-xs font-bold text-text-primary leading-tight">{member.name}</p>
            <p className="text-[9px] text-text-muted">{member.role}</p>
            {"twitter" in member && member.twitter && (
              <a
                href={`https://x.com/${member.twitter}`}
                target="_blank"
                rel="noreferrer"
                className="mt-1 inline-flex items-center gap-0.5 text-[8px] text-text-muted hover:text-primary transition-colors"
              >
                <svg viewBox="0 0 24 24" className="w-2.5 h-2.5 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                @{member.twitter}
              </a>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
