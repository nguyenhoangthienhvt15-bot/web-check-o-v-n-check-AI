import React from 'react';
import { Mail, ShieldCheck } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 py-6 px-4 transition-colors">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <span>Hệ thống phát triển bởi:</span>
          <strong className="text-gray-900 dark:text-gray-100 font-semibold">
            KS Nguyễn Hoàng Thiện [SYNAPES EDU]
          </strong>
        </div>

        <div className="flex items-center gap-2">
          <Mail className="w-4 h-4 text-red-500" />
          <a
            href="mailto:nguyenhoangthien.hvt.15@gmail.com"
            className="hover:text-blue-600 dark:hover:text-blue-400 font-mono transition-colors"
          >
            nguyenhoangthien.hvt.15@gmail.com
          </a>
        </div>
      </div>
    </footer>
  );
};

