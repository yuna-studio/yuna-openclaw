"use client";

import Image from "next/image";
import { motion } from "framer-motion";

const TEAM_MEMBERS = [
  {
    role: "CEO / 1인 개발자",
    name: "낭만코딩",
    desc: "대표인데 코딩함. (사실 혼자 다 함)",
    image: "/profile-nangman.jpg",
    color: "border-primary",
  },
  {
    role: "비서실장",
    name: "비서가재",
    desc: "일정 관리 & 멘탈 케어 담당",
    image: "/profile-secretary.jpg",
    color: "border-secondary",
  },
  {
    role: "수사부장",
    name: "탐정가재",
    desc: "버그 검거율 99%의 명탐정",
    image: "/profile-scout.jpg", // Scout -> Detective
    color: "border-accent-highlight",
  },
  {
    role: "법무팀장",
    name: "판사가재",
    desc: "엄격하고 근엄한 코드 리뷰어",
    image: "/profile-judge.jpg",
    color: "border-text-primary",
  },
];

export function OrgChart() {
  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h2 className="text-2xl font-bold text-text-primary mb-2">가재컴퍼니 조직도</h2>
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
            <p className="text-xs text-text-muted text-center break-keep px-2">
              {member.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
