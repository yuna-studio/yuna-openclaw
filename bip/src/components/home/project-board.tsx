"use client";

import { useEffect, useState } from "react";
import { collection, getDocs, query, orderBy, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion } from "framer-motion";

interface Project {
  id: string;
  title: string;
  desc: string;
  status: "dev" | "shipped" | "hold";
  link?: string;
}

const INITIAL_PROJECTS: Project[] = [
  { id: "1", title: "가재컴퍼니 사옥", desc: "홈페이지 리뉴얼 프로젝트", status: "dev", link: "/" },
  { id: "2", title: "비서가재 AI", desc: "텔레그램 봇 연동 시스템", status: "shipped", link: "#" },
  { id: "3", title: "탐정가재 로그 분석기", desc: "에러 로그 자동 분석 툴", status: "hold", link: "#" },
];

export function ProjectBoard() {
  const [projects, setProjects] = useState<Project[]>(INITIAL_PROJECTS);

  useEffect(() => {
    if (!db) return;

    const fetchProjects = async () => {
      try {
        const q = query(collection(db, "projects"), orderBy("createdAt", "desc"), limit(3));
        const snapshot = await getDocs(q);
        if (!snapshot.empty) {
            const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Project));
            setProjects(data);
        }
      } catch (e) {
        // Fallback to initial data silently
      }
    };
    
    fetchProjects();
  }, []);

  const getStatusBadge = (status: Project['status']) => {
    switch (status) {
      case 'dev': return <span className="text-[10px] bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full font-bold">🚧 개발중</span>;
      case 'shipped': return <span className="text-[10px] bg-green-100 text-green-800 px-2 py-0.5 rounded-full font-bold">🚀 배포완료</span>;
      case 'hold': return <span className="text-[10px] bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full font-bold">⏸️ 보류</span>;
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-12 border-t border-dashed border-border">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-text-primary">📌 프로젝트 현황</h2>
        <span className="text-xs text-text-muted font-mono animate-pulse">Live Updating...</span>
      </div>

      <div className="space-y-3">
        {projects.map((project) => (
          <motion.div
            key={project.id}
            initial={{ x: -10, opacity: 0 }}
            whileInView={{ x: 0, opacity: 1 }}
            viewport={{ once: true }}
            className="flex items-center justify-between p-4 bg-white border border-border rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                {getStatusBadge(project.status)}
                <h3 className="font-bold text-text-primary text-sm">{project.title}</h3>
              </div>
              <p className="text-xs text-text-secondary">{project.desc}</p>
            </div>
            {project.link && (
                <a href={project.link} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline">
                    구경하기
                </a>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
