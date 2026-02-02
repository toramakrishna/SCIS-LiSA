import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BookOpen, TrendingUp, Users, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function HomePage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: Search,
      title: 'Natural Language Query',
      description: 'Ask questions in plain English and get instant insights from publication data',
      action: () => navigate('/query'),
      buttonText: 'Try Query',
      gradient: 'from-blue-500 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30',
      border: 'border-l-blue-500',
    },
    {
      icon: Users,
      title: 'Faculty Directory',
      description: 'Browse faculty profiles, publications, and research collaborations',
      action: () => navigate('/faculty'),
      buttonText: 'View Faculty',
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30',
      border: 'border-l-purple-500',
    },
    {
      icon: TrendingUp,
      title: 'Analytics Dashboard',
      description: 'Visualize publication trends, citations, and research impact',
      action: () => navigate('/analytics'),
      buttonText: 'View Analytics',
      gradient: 'from-green-500 to-emerald-600',
      bgGradient: 'from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30',
      border: 'border-l-green-500',
    },
    {
      icon: BookOpen,
      title: 'Publication Database',
      description: 'Search and browse through comprehensive publication records',
      action: () => navigate('/query'),
      buttonText: 'Browse',
      gradient: 'from-orange-500 to-yellow-600',
      bgGradient: 'from-orange-50 to-yellow-50 dark:from-orange-950/30 dark:to-yellow-950/30',
      border: 'border-l-orange-500',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-12 px-4">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          SCISLiSA
        </h1>
        <p className="text-2xl font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent max-w-2xl mx-auto">
          School of Computer and Information Sciences - Library and Scholarly Analytics
        </p>
        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-3xl mx-auto font-medium">
          Explore publication data, analyze research trends, and gain insights into faculty contributions
          using natural language queries powered by AI.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card 
              key={feature.title} 
              className={`hover:shadow-xl hover:scale-[1.02] transition-all duration-300 border-l-4 ${feature.border} bg-gradient-to-br ${feature.bgGradient}`}
            >
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`p-3 bg-gradient-to-br ${feature.gradient} rounded-lg shadow-md`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-400 bg-clip-text text-transparent">
                    {feature.title}
                  </CardTitle>
                </div>
                <CardDescription className="text-slate-600 dark:text-slate-400 font-medium">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={feature.action} 
                  className={`w-full bg-gradient-to-r ${feature.gradient} hover:opacity-90 shadow-md`}
                >
                  {feature.buttonText}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Stats Section */}
      <Card className="border-l-4 border-l-indigo-500 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-950/30 dark:via-purple-950/30 dark:to-pink-950/30">
        <CardHeader>
          <CardTitle className="text-2xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Database Overview
          </CardTitle>
          <CardDescription className="text-slate-600 dark:text-slate-400 font-medium">
            Current statistics from our publication database
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg">
              <div className="text-4xl font-bold">1,301</div>
              <div className="text-sm opacity-90 font-medium">Publications</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg">
              <div className="text-4xl font-bold">1,090</div>
              <div className="text-sm opacity-90 font-medium">Authors</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-gradient-to-br from-pink-500 to-pink-600 text-white shadow-lg">
              <div className="text-4xl font-bold">34</div>
              <div className="text-sm opacity-90 font-medium">Faculty Members</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
