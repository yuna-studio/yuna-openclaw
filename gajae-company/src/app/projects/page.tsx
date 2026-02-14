import Link from "next/link";
import {
  CheckCircle2,
  CircleCheck,
  CircleX,
  GanttChartSquare,
  CalendarDays,
  Flag,
  ArrowRight,
} from "lucide-react";

const projects = [
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "1. PF",
    owner: "PM",
    status: "DONE",
    approval: "APPROVED",
    lastUpdated: "2026-02-06",
    commit: "",
    waiting: false,
  },
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "2. FBS",
    owner: "PO",
    status: "DONE",
    approval: "APPROVED",
    lastUpdated: "2026-02-06",
    commit: "https://github.com/yuna-studio/yuna-openclaw/commit/cff11de",
    waiting: false,
  },
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "3. RFD",
    owner: "UX",
    status: "DONE",
    approval: "APPROVED",
    lastUpdated: "2026-02-06",
    commit: "https://github.com/yuna-studio/yuna-openclaw/commit/f3d32c9",
    waiting: false,
  },
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "4. FBD",
    owner: "UX",
    status: "DONE",
    approval: "APPROVED",
    lastUpdated: "2026-02-06",
    commit: "https://github.com/yuna-studio/yuna-openclaw/commit/489b926",
    waiting: false,
  },
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "5. RFE/RFK",
    owner: "PM",
    status: "DONE",
    approval: "WAITING",
    lastUpdated: "2026-02-06",
    commit: "https://github.com/yuna-studio/yuna-openclaw/commit/f3d32c9",
    waiting: true,
  },
  {
    feature: "[GAJAE-BIP] Service-MVP v1.7",
    step: "6. 기술 구현",
    owner: "DEV",
    status: "INPROGRESS",
    approval: "WAITING",
    lastUpdated: "2026-02-06",
    commit: "",
    waiting: true,
  },
];

const getStatusChip = (status: string) => {
  if (status === "DONE") {
    return {
      icon: <CheckCircle2 size={14} />,
      cls: "bg-emerald-100 text-emerald-700 border-emerald-200",
      text: "완료",
    };
  }
  if (status === "INPROGRESS") {
    return {
      icon: <GanttChartSquare size={14} />,
      cls: "bg-blue-100 text-blue-700 border-blue-200",
      text: "진행중",
    };
  }
  return {
    icon: <CircleX size={14} />,
    cls: "bg-slate-100 text-slate-700 border-slate-200",
    text: status,
  };
};

const getApprovalChip = (approval: string) => {
  const isDone = approval === "APPROVED";
  return {
    icon: isDone ? <CircleCheck size={14} /> : <CalendarDays size={14} />,
    cls: isDone
      ? "bg-emerald-100 text-emerald-700 border-emerald-200"
      : "bg-amber-100 text-amber-700 border-amber-200",
    text: isDone ? "승인됨" : "승인 대기",
  };
};

export default function ProjectsPage() {
  const doneCount = projects.filter((p) => p.status === "DONE").length;
  const inProgressCount = projects.filter((p) => p.status === "INPROGRESS").length;
  const waitingCount = projects.filter((p) => p.waiting).length;

  return (
    <div className="container mx-auto px-6 py-12">
      <section className="mb-12">
        <p className="text-xs uppercase tracking-[0.2em] text-ghibli-blue font-black">Project Monitoring</p>
        <h1 className="text-4xl lg:text-6xl font-black mt-3 mb-4 text-ghibli-text">
          진행중인 개발 프로젝트
        </h1>
        <p className="text-slate-500 text-lg">
          현재 실행 중인 프로젝트의 단계별 상태와 CEO 승인 상태를 한 화면에서 확인합니다.
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        <div className="ghibli-card p-6 bg-white/80">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-black">완료 단계</p>
          <p className="text-3xl font-black text-ghibli-text mt-2">{doneCount} / {projects.length}</p>
        </div>
        <div className="ghibli-card p-6 bg-white/80">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-black">진행중</p>
          <p className="text-3xl font-black text-ghibli-text mt-2">{inProgressCount}</p>
        </div>
        <div className="ghibli-card p-6 bg-white/80">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-black">승인 대기</p>
          <p className="text-3xl font-black text-ghibli-text mt-2">{waitingCount}</p>
        </div>
      </section>

      <section className="overflow-x-auto mb-8">
        <table className="w-full min-w-[760px] text-left bg-white/80 border-2 border-slate-200">
          <thead>
            <tr className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
              <th className="py-3 px-4 border-b border-slate-200">피처</th>
              <th className="py-3 px-4 border-b border-slate-200">단계</th>
              <th className="py-3 px-4 border-b border-slate-200">담당</th>
              <th className="py-3 px-4 border-b border-slate-200">진행</th>
              <th className="py-3 px-4 border-b border-slate-200">승인</th>
              <th className="py-3 px-4 border-b border-slate-200">최종 업데이트</th>
              <th className="py-3 px-4 border-b border-slate-200">증빙 커밋</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((item) => {
              const statusChip = getStatusChip(item.status);
              const approvalChip = getApprovalChip(item.approval);
              return (
                <tr key={`${item.step}`} className="border-b border-slate-100">
                  <td className="py-4 px-4 font-black text-sm">{item.feature}</td>
                  <td className="py-4 px-4 text-xs">
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full border-2 border-slate-200 bg-slate-50 font-black">
                      <Flag size={12} />
                      {item.step}
                    </span>
                  </td>
                  <td className="py-4 px-4">{item.owner}</td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${statusChip.cls} font-black text-xs uppercase`}> 
                      {statusChip.icon}
                      {statusChip.text}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${approvalChip.cls} font-black text-xs uppercase`}> 
                      {approvalChip.icon}
                      {approvalChip.text}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-sm text-slate-500">{item.lastUpdated}</td>
                  <td className="py-4 px-4 text-sm">
                    {item.commit ? (
                      <a
                        href={item.commit}
                        className="inline-flex items-center gap-2 text-ghibli-blue font-black hover:underline"
                        target="_blank"
                        rel="noreferrer"
                      >
                        보기
                      </a>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>

      <section className="flex items-center justify-between border-t border-slate-200 pt-5">
        <p className="text-sm text-slate-500">
          기준 문서: <a href="https://github.com/yuna-studio/yuna-openclaw/blob/main/docs/pm/GATE.md" target="_blank" rel="noreferrer" className="text-ghibli-accent font-black">docs/pm/GATE.md</a>
        </p>
        <Link href="/timeline" className="inline-flex items-center gap-2 text-ghibli-blue font-black text-sm uppercase tracking-wider">
          연대기도 같이 보기 <ArrowRight size={14} />
        </Link>
      </section>
    </div>
  );
}
