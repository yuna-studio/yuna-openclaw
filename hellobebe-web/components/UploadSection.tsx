"use client";

import { motion } from "framer-motion";
import { Upload, Image as ImageIcon, CheckCircle2, ChevronRight } from "lucide-react";

export default function UploadSection({ onComplete }: { onComplete?: () => void }) {
  return (
    <section className="py-24 px-4 bg-[var(--color-bg-main)]">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-serif text-[var(--color-text-main)] mb-6">
            초음파 사진 업로드
          </h2>
          <p className="text-gray-500 max-w-xl mx-auto">
            정면이 잘 보이는 입체 초음파 사진일수록 <br />
            더욱 선명하고 정확한 실사화가 가능합니다.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* Guide Area */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
              <h3 className="font-bold flex items-center gap-2 mb-4">
                <CheckCircle2 className="text-[var(--color-success)] w-5 h-5" />
                좋은 사진 가이드
              </h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li>• 아기의 얼굴 정면이 명확하게 보이는 사진</li>
                <li>• 코와 입술의 윤곽이 뚜렷한 사진</li>
                <li>• 노이즈가 적고 선명한 3D/4D 초음파 사진</li>
              </ul>
            </div>
            
            <div className="bg-red-50 p-6 rounded-2xl border border-red-100">
              <h3 className="font-bold flex items-center gap-2 mb-4 text-red-700">
                유의사항
              </h3>
              <p className="text-xs text-red-600 leading-relaxed">
                손으로 얼굴을 가리고 있거나 정면이 아닌 경우 AI 분석이 어려울 수 있습니다. 이 경우 티켓이 차감되지 않습니다.
              </p>
            </div>
          </div>

          {/* Upload Area */}
          <motion.div 
            whileHover={{ scale: 1.01 }}
            className="relative aspect-square bg-white border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center p-12 cursor-pointer hover:border-[var(--color-primary)] transition-colors group"
          >
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6 group-hover:bg-blue-50 transition-colors">
              <Upload className="w-8 h-8 text-slate-400 group-hover:text-[var(--color-primary)] transition-colors" />
            </div>
            <p className="font-bold text-lg mb-2">사진 선택 또는 드래그</p>
            <p className="text-sm text-gray-400">JPG, PNG, WebP (최대 10MB)</p>
            
            <input 
              type="file" 
              className="absolute inset-0 opacity-0 cursor-pointer" 
              onChange={onComplete}
            />
          </motion.div>
        </div>

        {/* Mock Helper for Testing */}
        <div className="mt-12 flex justify-center">
          <button 
            onClick={onComplete}
            className="text-slate-400 text-sm hover:text-[var(--color-primary)] transition-colors flex items-center gap-2"
          >
            가이드 확인 완료, 다음으로 <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
