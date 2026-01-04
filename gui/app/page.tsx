'use client';
import YbDashboard from '@/components/YbDashboard';

export default function Page() {
  return (
    <div className="h-full w-full text-white">
      {/* UI Factory가 만든 대시보드 부품을 여기에 장착 */}
      <YbDashboard />
    </div>
  );
}
