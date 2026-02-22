"use client";

import Image from "next/image";
import { motion } from "framer-motion";

const TEAM = [
  {
    name: "낭만코딩",
    role: "CEO",
    image: "/profile-nangman.jpg",
    color: "border-primary",
  },
  {
    name: "비서가재 AI",
    role: "OpenClaw · M2 맥미니",
    image: "/profile-secretary.jpg",
    color: "border-orange-400",
  },
  {
    name: "홈 AI",
    role: "맥북 프로",
    image: "/profile-home.jpeg",
    color: "border-emerald-400",
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
          1명의 사람과 2개의 AI.
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
      <div className="grid grid-cols-3 gap-6 max-w-xs mx-auto">
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
          </motion.div>
        ))}
      </div>
    </div>
  );
}
