import { NavLink } from 'react-router-dom';
import { Home, Search, GraduationCap, Users, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Home', path: '/', icon: Home, gradient: 'from-blue-500 to-indigo-600', color: 'text-blue-600' },
  { name: 'Query', path: '/query', icon: Search, gradient: 'from-purple-500 to-pink-600', color: 'text-purple-600' },
  { name: 'Faculty', path: '/faculty', icon: Users, gradient: 'from-green-500 to-emerald-600', color: 'text-green-600' },
  { name: 'Students', path: '/students', icon: GraduationCap, gradient: 'from-orange-500 to-yellow-600', color: 'text-orange-600' },
  { name: 'Admin', path: '/admin', icon: Settings, gradient: 'from-red-500 to-orange-600', color: 'text-red-600' },
];

export function Sidebar() {
  return (
    <aside className="w-full md:w-64 border-b md:border-b-0 md:border-r bg-gradient-to-r md:bg-gradient-to-b from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-950/30">
      <nav className="flex flex-row md:flex-col gap-2 p-2 md:p-4 overflow-x-auto md:overflow-x-visible">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 md:gap-3 rounded-lg px-3 py-2 text-xs md:text-sm font-medium transition-all duration-200 whitespace-nowrap',
                  isActive
                    ? `bg-gradient-to-r ${item.gradient} text-white shadow-md scale-[1.02]`
                    : `${item.color} dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 hover:scale-[1.02] hover:shadow-sm`
                )
              }
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
