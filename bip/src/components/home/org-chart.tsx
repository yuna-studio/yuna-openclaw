"use client";

import Image from "next/image";
import { motion } from "framer-motion";

const TEAM_MEMBERS = [
  {
    role: "CEO / Director",
    name: "낭만코딩",
    desc: ["디렉팅부터 개발까지", "혼자 다 하는 1인 스튜디오"],
    badge: null,
    image: "/profile-nangman.jpg",
    color: "border-primary",
    twitter: "romantic_coding",
  },
  {
    role: "비서실장 / 만능 오른팔",
    name: "비서가재 🦞",
    desc: ["기획, 코딩, 문서, 운영", "시키면 다 하는 진짜 만능 AI"],
    badge: "Powered by OpenClaw",
    image: "/profile-secretary.jpg",
    color: "border-secondary",
  },
  {
    role: "수사부 / 실무 담당",
    name: "탐정가재 🔍",
    desc: ["웹 검색, 코드 작성, 리서치", "시키는 건 뭐든 해오는 일꾼"],
    badge: null,
    image: "/profile-scout.jpg",
    color: "border-accent-highlight",
  },
  {
    role: "법무부 / 품질 검수",
    name: "판사가재 ⚖️",
    desc: ["탐정이 해온 결과물 검수", "통과 못 하면 가차없이 반려"],
    badge: null,
    image: "/profile-judge.jpg",
    color: "border-text-primary",
  },
];

export function OrgChart() {
  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h2 className="text-2xl font-bold text-text-primary mb-2">가재 컴퍼니 조직도</h2>
        <p className="text-text-secondary text-sm">체계적인 척하지만 사실은 우당탕탕 1인 개발팀입니다.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {TEAM_MEMBERS.map((member, idx) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            viewport={{ once: true }}
            className="flex flex-col items-center group cursor-pointer"
          >
            <div className={`relative w-24 h-24 md:w-32 md:h-32 mb-4 rounded-full overflow-hidden border-4 ${member.color} shadow-lg group-hover:scale-105 transition-transform duration-300`}>
              <Image
                src={member.image}
                alt={member.name}
                fill
                className="object-cover"
              />
            </div>
            <span className="text-xs font-bold text-primary mb-1 bg-primary-light px-2 py-0.5 rounded-full">
              {member.role}
            </span>
            <h3 className="font-bold text-text-primary text-lg mb-1">{member.name}</h3>
            <p className="text-xs text-text-muted text-center px-2">
              {member.desc.map((line, i) => (
                <span key={i}>
                  {line}
                  {i < member.desc.length - 1 && <br />}
                </span>
              ))}
            </p>
            {member.badge && (
              <span className="mt-1.5 text-[8px] font-mono text-text-muted/60 bg-gray-100 px-1.5 py-0.5 rounded">
                {member.badge}
              </span>
            )}
            {"twitter" in member && member.twitter && (
              <a
                href={`https://x.com/${member.twitter}`}
                target="_blank"
                rel="noreferrer"
                className="mt-1.5 inline-flex items-center gap-1 text-[10px] text-text-muted hover:text-primary transition-colors"
              >
                <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current" aria-label="X"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                @{member.twitter}
              </a>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
